"""Pure/offline regression checks for isolated server-only forward epoch recording."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

FILE = Path(__file__).resolve().parents[1] / "prospective_epoch_capture_v1.py"
SPEC = importlib.util.spec_from_file_location("prospective_epoch_recorder", FILE)
assert SPEC is not None and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
UTC = timezone.utc


def test_archive_selection_exact_age_and_no_future(tmp_path):
    folder = tmp_path / "2026" / "09" / "25"
    folder.mkdir(parents=True)
    cutoff = datetime(2026, 9, 25, 11, 45, tzinfo=UTC)
    (folder / "20260925T114000000000Z_a.jsonl").write_text("fixture\n")
    (folder / "20260925T114500000001Z_future.jsonl").write_text("fixture\n")
    f, age, status = mod.latest_snapshot_file(cutoff, tmp_path)
    assert status == "VALID_CONTEXT" and age == 300
    assert f.name.endswith("_a.jsonl")
    (folder / "20260925T114000000000Z_a.jsonl").unlink()
    assert mod.latest_snapshot_file(cutoff, tmp_path)[2] == "MISSING_CONTEXT"


@pytest.mark.parametrize("tf", list(mod.DEPTHS))
def test_latest_closed_bar_is_not_open_bar(tf):
    step = mod.STEP[tf]
    cutoff = 36*86400000 + 11*3600000 + 15*60000
    last = (cutoff // step - 1)*step
    bars = [{"open_time_ms": last-step, "close_time_ms": last-1, "closed": 1,
             "ingested_at_ms": last + 2*step},
            {"open_time_ms": last, "close_time_ms": last+step-1, "closed": 1,
             "ingested_at_ms": last+step+1000},
            {"open_time_ms": last+step, "close_time_ms": last+2*step-1, "closed": 0,
             "ingested_at_ms": last+2*step+1000}]
    selected, flags = mod.bar_window(bars, tf, cutoff, 2, 180000)
    assert selected[-1]["open_time_ms"] == last
    assert not any(x in flags for x in ("LOOKAHEAD_OR_UNCLOSED", "MISSING_LAST_CLOSED_BAR"))


def test_missing_depth_and_gap_fail_closed():
    cutoff = 10 * mod.STEP["15m"]
    rows = [{"open_time_ms": i*mod.STEP["15m"], "close_time_ms": (i+1)*mod.STEP["15m"]-1,
             "closed": 1, "ingested_at_ms": cutoff+1000} for i in (6,7,9)]
    _, reasons = mod.bar_window(rows, "15m", cutoff, 4, 180000)
    assert "INSUFFICIENT_DEPTH" in reasons
    assert "HISTORY_GAP" in reasons


def test_ingest_time_is_separate_gate():
    cutoff = 10 * mod.STEP["15m"]
    rows = [{"open_time_ms": i*mod.STEP["15m"], "close_time_ms": (i+1)*mod.STEP["15m"]-1,
             "closed": 1, "ingested_at_ms": cutoff+180001} for i in range(8,10)]
    _, reasons = mod.bar_window(rows, "15m", cutoff, 2, 180000)
    assert reasons == ["LATE_OR_UNKNOWN_INGESTION"]


def test_registration_requires_separate_namespace_and_pins(tmp_path, monkeypatch):
    root = tmp_path / "prospective_epochs"
    epoch = root / "epoch_test"
    epoch.mkdir(parents=True)
    monkeypatch.setattr(mod, "ROOT", root)
    files = {}
    for key in ("ANCHOR", "OLD_LEDGER", "HARNESS", "PROTOCOL"):
        f = tmp_path / (key+".txt")
        f.write_text("{}" if key=="ANCHOR" else key)
        files[key] = f
        monkeypatch.setattr(mod, key, f)
    files["ANCHOR"].write_text('{"resolved_primary_families":54}')
    monkeypatch.setattr(mod, "HARNESS_SHA", mod.sha_file(files["HARNESS"]))
    monkeypatch.setattr(mod, "PROTOCOL_SHA", mod.sha_file(files["PROTOCOL"]))
    codefile = tmp_path / "recorder.py"
    codefile.write_text("fixture immutable source")
    registration = {
        "schema_version": "ktrader.phase11g.prospective_epoch.registration.v1",
        "epoch_id": "epoch_test",
        "classification": "FORWARD_FIRST_SEEN_DATA_ONLY",
        "provider_id": "binance_usdm",
        "panel_rule": "FIRST_19_RECORDED_RANKS_NO_SUBSTITUTION",
        "panel_size": 19, "settle_seconds": 180, "max_capture_delay_seconds": 300,
        "original_resolved_families": 54, "strategy_evaluation_enabled": False,
        "trading_authorized": False, "holdout_opened": False, "hp_omen_allowed": False,
        "admitted_new_prospective_families": 0,
        "old_harness_sha256": mod.HARNESS_SHA, "old_protocol_sha256": mod.PROTOCOL_SHA,
        "old_anchor_sha256": mod.sha_file(files["ANCHOR"]),
        "old_ledger_sha256": mod.sha_file(files["OLD_LEDGER"]),
        "recorder_sha256": mod.sha_file(codefile),
        "registered_at_utc": "2026-09-25T11:00:00Z",
        "start_cutoff_utc": "2026-09-25T11:30:00Z",
        "end_cutoff_utc": "2026-09-25T12:00:00Z",
    }
    regpath = epoch / "registration.json"
    regpath.write_text(json.dumps(registration))
    assert mod.validate_registration(regpath, codefile)[0]["epoch_id"] == "epoch_test"
    registration["old_ledger_sha256"] = "0"*64
    regpath.write_text(json.dumps(registration))
    with pytest.raises(ValueError, match="pinned source changed"):
        mod.validate_registration(regpath, codefile)
    registration["old_ledger_sha256"] = mod.sha_file(files["OLD_LEDGER"])
    registration["start_cutoff_utc"] = "2026-09-25T11:15:00Z"
    regpath.write_text(json.dumps(registration))
    with pytest.raises(ValueError, match="strictly future"):
        mod.validate_registration(regpath, codefile)


def test_previously_written_cutoff_collision_is_never_overwritten(tmp_path):
    f = tmp_path / "already.json"
    mod.immutable_json(f, {"status": "FIRST_SEEN"})
    with pytest.raises(FileExistsError):
        mod.immutable_json(f, {"status": "REWRITTEN"})
    assert json.loads(f.read_text()) == {"status": "FIRST_SEEN"}


def test_exact_closed_utc_boundaries():
    t = datetime(2026, 9, 25, 11, 5, 0, tzinfo=UTC)
    assert mod.next_closed_start(t) == datetime(2026, 9, 25, 11, 30, tzinfo=UTC)
    with pytest.raises(ValueError):
        mod.utc("2026-09-25T11:30:00+03:00")
