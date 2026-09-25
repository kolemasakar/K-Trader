"""Offline safety regressions for isolated Phase 11G retrospective auditor."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from datetime import datetime, timedelta, timezone
import pytest

MODULE_FILE = Path(__file__).resolve().parents[1] / "audit_retrospective_gap_v1.py"
SPEC = importlib.util.spec_from_file_location("retro_gap_audit", MODULE_FILE)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def series(tf, first, last, late=False):
    step = mod.STEPS_MS[tf]
    result = [(i*step, (i+1)*step - 1,
               ((i+1)*step + (180001 if late and i == last else 1000)),
               "provider") for i in range(first, last+1)]
    return [r[0] for r in result], result


@pytest.mark.parametrize("tf", ["1d", "4h", "1h", "15m", "5m"])
def test_excludes_bar_still_open_at_m15_boundary(tf):
    step = mod.STEPS_MS[tf]
    cutoff = 10*step + (900000 if tf not in ("15m", "5m") else 0)
    last_closed_open_index = cutoff // step - 1
    opens, rows = series(tf, last_closed_open_index-2, last_closed_open_index+1)
    ok, why, _ = mod.assess_window(opens, rows, cutoff, tf, 3)
    assert ok and not why


def test_missing_depth_is_explicit():
    step = mod.STEPS_MS["15m"]
    opens, rows = series("15m", 7, 9)
    ok, why, _ = mod.assess_window(opens, rows, 10*step, "15m", 4)
    assert not ok
    assert "INSUFFICIENT_DEPTH" in why


def test_history_gap_is_fail_closed():
    step = mod.STEPS_MS["15m"]
    opens, rows = series("15m", 5, 9)
    filtered = [r for i, r in enumerate(rows) if i != 2]
    ok, why, _ = mod.assess_window([r[0] for r in filtered], filtered, 10*step, "15m", 4)
    assert not ok
    assert "HISTORY_GAP" in why


def test_ingestion_metadata_does_not_upgrade_late_bars():
    step = mod.STEPS_MS["15m"]
    opens, rows = series("15m", 5, 9)
    late = list(rows)
    last = late[-1]
    late[-1] = (last[0], last[1], 10*step + 180001, last[3])
    ok, why, tag = mod.assess_window(opens, late, 10*step, "15m", 5)
    assert ok and not why
    assert tag == "LATE_CURRENT_DB_INGESTION"


def test_snapshot_exact_age_and_future_fail_closed():
    cutoff = datetime(2026, 9, 25, 10, 15, tzinfo=timezone.utc)
    assert mod.snapshot_choice([cutoff-timedelta(seconds=300)], cutoff)[1] == "VALID_CONTEXT"
    assert mod.snapshot_choice([cutoff-timedelta(seconds=301)], cutoff)[1] == "STALE_CONTEXT"
    assert mod.snapshot_choice([cutoff+timedelta(seconds=1)], cutoff)[1] == "MISSING_CONTEXT"


def test_archive_timestamp_is_cutoff_stable():
    cutoff = datetime(2026, 9, 25, 10, 15, tzinfo=timezone.utc)
    assert mod.archive_file_timestamp("20260925T101039123329Z_abc.jsonl") <= cutoff
    assert mod.archive_file_timestamp("20260925T102039123329Z_abc.jsonl") > cutoff
    with pytest.raises(ValueError):
        mod.archive_file_timestamp("unparseable.jsonl")


def test_asof_must_be_utc_closed_m15_boundary():
    assert mod.parse_utc("2026-09-25T10:15:00Z").minute == 15
    for value in ["2026-09-25T10:13:00Z", "2026-09-25T10:15:01Z",
                  "2026-09-25T10:15:00", "2026-09-25T10:15:00+03:00"]:
        with pytest.raises(ValueError):
            mod.parse_utc(value)
