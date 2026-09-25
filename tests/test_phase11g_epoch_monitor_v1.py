"""Focused regression tests for server-local Phase 11G epoch monitor."""
import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

MODULE = Path(__file__).resolve().parents[1] / "phase11g_epoch_monitor_v1.py"
SPEC = importlib.util.spec_from_file_location("phase11g_monitor", MODULE)
monitor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitor)
UTC = timezone.utc


def test_schedule_has_24_hourly_5_deep_one_final():
    scheduled = monitor.schedule()
    assert len(scheduled) == 30
    assert sum(kind == "HOURLY" for _, kind in scheduled) == 24
    assert sum(kind == "DEEP" for _, kind in scheduled) == 5
    assert sum(kind == "FINAL" for _, kind in scheduled) == 1
    assert scheduled[0] == (monitor.START_HOURLY, "HOURLY")
    assert scheduled[-1] == (monitor.FINAL, "FINAL")


def test_no_backfill_only_deadline_passed():
    first = monitor.FIRST
    assert monitor.expected_cutoffs(first + timedelta(minutes=4)) == []
    assert monitor.expected_cutoffs(first + timedelta(minutes=5)) == [first]
    assert len(monitor.expected_cutoffs(monitor.FINAL)) == 96


def test_immutable_reports_refuse_to_overwrite(tmp_path):
    dest = tmp_path / "checkpoint.json"
    monitor.immutable_report(dest, {"status": "PASS"})
    with pytest.raises(FileExistsError):
        monitor.immutable_report(dest, {"status": "REWRITTEN"})
    assert json.loads(dest.read_text())["status"] == "PASS"


def test_missing_immutable_manifest_fails_closed(tmp_path):
    cutoff = monitor.FIRST
    res = monitor.inspect_cutoff(tmp_path, cutoff, deep=True, events_by_cutoff={})
    assert res["status"] == "FAIL_CLOSED"
    assert "MISSING_IMMUTABLE_MANIFEST" in res["failures"]


def test_frozen_source_hash_mismatch_fails(tmp_path, monkeypatch):
    e = tmp_path / "epoch"
    b = tmp_path / "base"
    e.mkdir()
    (b / "combined_rules/current_state_manifests").mkdir(parents=True)
    (b / "combined_rules/prospective_v2_2_ledger").mkdir(parents=True)
    (b / "harness").mkdir()
    for key, file in [
        ("EXPECTED_REG_SHA", e/"registration.json"),
        ("EXPECTED_RECORDER_SHA", e/"prospective_epoch_capture_v1.py"),
        ("EXPECTED_ANCHOR_SHA", b/"combined_rules/current_state_manifests/20260918T061500Z.json"),
        ("EXPECTED_LEDGER_SHA", b/"combined_rules/prospective_v2_2_ledger/deduplicated_events.jsonl"),
        ("EXPECTED_HARNESS_SHA", b/"harness/candidate_v2_2_backtest.py"),
        ("EXPECTED_PROTOCOL_SHA", b/"protocol.json"),
    ]:
        file.write_text("source")
        monkeypatch.setattr(monitor, key, monitor.sha(file))
    assert all(monitor.frozen_pins(e, b).values())
    (e/"registration.json").write_text("tampered")
    assert monitor.frozen_pins(e, b)["registration"] is False


def test_final_check_requires_complete_boundary(tmp_path, monkeypatch):
    monkeypatch.setattr(monitor, "frozen_pins", lambda root: {"test": True})
    monkeypatch.setattr(monitor, "get_health", lambda: {
        "status": "ok", "mode": "read_only", "provider": "binance_usdm", "data_ready": True})
    monkeypatch.setattr(monitor, "exact_runner_pids", lambda: [])
    (tmp_path/"events.jsonl").write_text(json.dumps(
        {"event": "REGISTERED_RUNNER_START", "first_cutoff": monitor.iso(monitor.FIRST)}
    ) + "\n")
    (tmp_path/"status.json").write_text('{"status":"WAITING"}')
    result = monitor.review(tmp_path, monitor.FINAL, "FINAL")
    assert result["status"] == "FAIL_CLOSED"
    assert "NOT_COMPLETE_BOUNDARY" in result["failure_reasons"]


def test_current_hourly_keeps_legacy_history_read_only(tmp_path, monkeypatch):
    monkeypatch.setattr(monitor, "frozen_pins", lambda root: {"anchor": True, "ledger": True})
    monkeypatch.setattr(monitor, "get_health", lambda: {
        "status": "ok", "mode": "read_only", "provider": "binance_usdm", "data_ready": True})
    monkeypatch.setattr(monitor, "exact_runner_pids", lambda: [123])
    (tmp_path/"events.jsonl").write_text(json.dumps(
        {"event": "REGISTERED_RUNNER_START", "first_cutoff": monitor.iso(monitor.FIRST)}
    ) + "\n")
    result = monitor.review(tmp_path, monitor.FIRST + timedelta(minutes=4), "BASELINE")
    assert result["status"] == "PASS"
    assert result["expected_cutoffs"] == 0
    assert result["prospective_families_admitted"] == 0
    assert result["notifications_scheduled"] is False
