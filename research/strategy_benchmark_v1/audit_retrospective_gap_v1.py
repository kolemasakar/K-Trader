#!/usr/bin/env python3
"""Read-only, server-only Phase 11G retrospective gap coverage audit.

NO outcome replay. NO prospective ledger mutation. NO HP-OMEN dependency.
SQLite is opened mode=ro/query_only. Canonical universe digest verification
uses the installed K-Trader ktrader.history.universe loader.
"""
from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace

SCHEMA = "ktrader.phase11g.recovery_retrospective.coverage.v1"
PROVIDER = "binance_usdm"
REQUIRED = {"1d": 20, "4h": 80, "1h": 300, "15m": 400, "5m": 20}
STEPS_MS = {"1d": 86400000, "4h": 14400000, "1h": 3600000, "15m": 900000, "5m": 300000}


def parse_utc(value: str) -> datetime:
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None or d.utcoffset() != timedelta(0):
        raise ValueError("cutoffs must be explicitly UTC")
    if d.second != 0 or d.microsecond != 0 or d.minute % 15 != 0:
        raise ValueError("cutoffs must be closed M15 boundaries")
    return d


def milliseconds(d: datetime) -> int:
    return int(d.timestamp() * 1000)


def archive_file_timestamp(filename: str) -> datetime:
    # Immutable per-snapshot capture filename, e.g. 20260925T101039123329Z_<id>.jsonl.
    stamp = filename.split("_", 1)[0]
    return datetime.strptime(stamp, "%Y%m%dT%H%M%S%fZ").replace(tzinfo=timezone.utc)


def snapshot_choice(times: list[datetime], cutoff: datetime, max_age_seconds: int = 300):
    i = bisect_right(times, cutoff) - 1
    if i < 0:
        return None, "MISSING_CONTEXT"
    delta = (cutoff - times[i]).total_seconds()
    if delta < 0 or delta > max_age_seconds:
        return None, "STALE_CONTEXT"
    return i, "VALID_CONTEXT"


def assess_window(
    opens: list[int], rows: list[tuple[int, int, int | None, str | None]],
    cutoff_ms: int, tf: str, required_depth: int, settlement_ms: int = 180000,
):
    """Use only causal closed bars; return separate structure/ingest-timing results."""
    step = STEPS_MS[tf]
    # A bar that opens at cutoff is NOT closed. Last valid bar closes at cutoff-1ms.
    expected_last_open = (cutoff_ms // step - 1) * step
    expected_last_close = expected_last_open + step - 1
    # H1/4H/D1 bars opened before the M15 cutoff can still be in progress.
    # Never include any bar opening after the last FULLY closed interval.
    idx = bisect_right(opens, expected_last_open)
    window = rows[max(0, idx - required_depth):idx]
    reasons: list[str] = []
    if len(window) != required_depth:
        reasons.append("INSUFFICIENT_DEPTH")
    if not window or window[-1][1] != expected_last_close:
        reasons.append("MISSING_EXPECTED_LAST_CLOSE")
    if any(close != op + step - 1 for op, close, _, _ in window):
        reasons.append("INVALID_CLOSE_BOUNDARY")
    if any(right[0] - left[0] != step for left, right in zip(window, window[1:])):
        reasons.append("HISTORY_GAP")
    if any(close >= cutoff_ms for _, close, _, _ in window):
        reasons.append("FUTURE_CLOSE")
    structural_ok = not reasons
    provenance = "NOT_EVALUATED"
    if structural_ok:
        if any(ingest is None or ingest <= 0 for _, _, ingest, _ in window):
            provenance = "INGEST_TIMESTAMP_UNAVAILABLE"
        elif any(ingest > cutoff_ms + settlement_ms for _, _, ingest, _ in window):
            provenance = "LATE_CURRENT_DB_INGESTION"
        else:
            provenance = "INGEST_TIMESTAMPS_COMPATIBLE"
    return structural_ok, reasons, provenance


def self_test() -> None:
    step = STEPS_MS["15m"]
    cutoff = 10 * step
    rows = [(i * step, (i + 1) * step - 1, (i + 1) * step + 1000, "provider") for i in range(5, 10)]
    opens = [x[0] for x in rows]
    assert assess_window(opens, rows, cutoff, "15m", 5)[0:2] == (True, [])
    assert assess_window(opens, rows, cutoff, "15m", 5)[2] == "INGEST_TIMESTAMPS_COMPATIBLE"
    late = rows.copy()
    late[-1] = (late[-1][0], late[-1][1], cutoff + 180001, "provider")
    assert assess_window(opens, late, cutoff, "15m", 5)[2] == "LATE_CURRENT_DB_INGESTION"
    assert "INSUFFICIENT_DEPTH" in assess_window(opens, rows, cutoff, "15m", 6)[1]
    bad = rows.copy()
    bad[2] = (bad[2][0] + 30000, bad[2][1] + 30000, bad[2][2], "provider")
    assert "HISTORY_GAP" in assess_window([x[0] for x in bad], bad, cutoff, "15m", 5)[1]
    t = datetime(2026, 9, 25, 10, 15, tzinfo=timezone.utc)
    assert snapshot_choice([t-timedelta(seconds=300)], t)[1] == "VALID_CONTEXT"
    assert snapshot_choice([t-timedelta(seconds=301)], t)[1] == "STALE_CONTEXT"
    assert snapshot_choice([t+timedelta(seconds=1)], t)[1] == "MISSING_CONTEXT"
    assert archive_file_timestamp("20260925T101039123329Z_abc.jsonl") < t
    assert archive_file_timestamp("20260925T102039123329Z_abc.jsonl") > t
    # The 10:00 hourly bar is still OPEN at 10:15; the last closed is 09:00.
    hstep = STEPS_MS["1h"]
    m15_cutoff = 10 * hstep + STEPS_MS["15m"]
    hrows = [(i*hstep,(i+1)*hstep-1,(i+1)*hstep+1000,"provider") for i in range(7,11)]
    ok, why, _ = assess_window([x[0] for x in hrows], hrows, m15_cutoff, "1h", 3)
    assert ok and not why
    dstep = STEPS_MS["1d"]
    dcutoff = 10*dstep + STEPS_MS["15m"]
    drows = [(i*dstep,(i+1)*dstep-1,(i+1)*dstep+1000,"provider") for i in range(7,11)]
    ok, why, _ = assess_window([x[0] for x in drows], drows, dcutoff, "1d", 3)
    assert ok and not why
    print("SELF_TEST=PASS (11 checks)")


def run(args: argparse.Namespace) -> dict:
    from ktrader.history.universe import load_universe_archive

    start, end = parse_utc(args.start), parse_utc(args.end)
    if end < start:
        raise ValueError("end must not precede start")
    if args.panel_size < 1 or args.panel_size > 50:
        raise ValueError("panel_size outside 1..50")
    if args.settlement_seconds < 0:
        raise ValueError("negative settlement not supported")

    root = Path(args.research_root)
    source = root / "universe" / PROVIDER
    if not source.is_dir():
        raise FileNotFoundError(source)
    dates = set()
    d = (start - timedelta(days=1)).date()
    while d <= end.date():
        dates.add((d.year, d.month, d.day))
        d += timedelta(days=1)
    files = []
    for year, month, day in sorted(dates):
        directory = source / f"{year:04d}" / f"{month:02d}" / f"{day:02d}"
        files.extend(directory.glob("*.jsonl") if directory.is_dir() else [])
    files.sort()

    snapshot_times: list[datetime] = []
    snapshots = []
    archive_errors = []
    archive_file_count = 0
    manifest_hash = hashlib.sha256()
    first_config = None
    for f in files:
        relative = f.relative_to(root).as_posix()
        try:
            file_time = archive_file_timestamp(f.name)
        except ValueError:
            if len(archive_errors) < 20:
                archive_errors.append({"file": relative, "error": "INVALID_ARCHIVE_FILENAME"})
            continue
        # Strictly bound the input manifest to a FIXED interval; otherwise
        # later ongoing production captures mutate its digest between reruns.
        if not (start - timedelta(minutes=10) <= file_time <= end):
            continue
        raw = f.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        manifest_hash.update(json.dumps([relative, digest], ensure_ascii=True, separators=(",", ":")).encode("ascii") + b"\n")
        archive_file_count += 1
        try:
            verified = load_universe_archive(f)
            if verified.provider_id != PROVIDER or len(verified.snapshots) != 1:
                raise ValueError("unexpected provider or snapshot count")
            if first_config is None:
                first_config = verified.config
            if verified.config != first_config:
                raise ValueError("universe config drift")
            snap = verified.snapshots[0]
            if snap.captured_at != file_time:
                raise ValueError("archive filename and canonical captured_at mismatch")
            if snapshot_times and snap.captured_at <= snapshot_times[-1]:
                raise ValueError("non-increasing/duplicate snapshot timestamp")
            snapshot_times.append(snap.captured_at)
            snapshots.append(snap)
        except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
            if len(archive_errors) < 20:
                archive_errors.append({"file": relative, "error": type(exc).__name__, "message": str(exc)[:160]})

    # Each retained valid universe record has exact immutable ranks, verified by
    # canonical loader; never substitute lower-ranked members for failed slots.
    symbols = sorted({m.instrument.symbol for s in snapshots for m in s.members[:args.panel_size]})
    series = {}
    conn = sqlite3.connect(f"file:{args.sqlite_db}?mode=ro", uri=True, timeout=8)
    conn.execute("PRAGMA query_only=ON")
    source_rows_sha = hashlib.sha256()
    source_rows = 0
    earliest = milliseconds(start)
    latest = milliseconds(end)
    try:
        conn.execute("BEGIN")
        for sym in symbols:
            for tf, n in REQUIRED.items():
                step = STEPS_MS[tf]
                # Extra slack permits explicit detection of gaps and missing depth.
                lower = earliest - (n + 8) * step
                tuples = conn.execute(
                    "SELECT open_time_ms,close_time_ms,ingested_at_ms,source_kind "
                    "FROM candles WHERE provider_id=? AND symbol=? AND interval=? "
                    "AND closed=1 AND open_time_ms>=? AND open_time_ms<? "
                    "ORDER BY open_time_ms",
                    (PROVIDER, sym, tf, lower, latest),
                ).fetchall()
                rows = [(int(op), int(close), int(ingest) if ingest is not None else None, kind)
                        for op, close, ingest, kind in tuples]
                series[(sym, tf)] = ([x[0] for x in rows], rows)
                source_rows += len(rows)
                for row in rows:
                    source_rows_sha.update(
                        json.dumps([sym, tf, *row], separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"
                    )
        daily = defaultdict(Counter)
        reason_counts = Counter()
        provenance_counts = Counter()
        overall = Counter()
        cutoffs_total = int((end-start).total_seconds() // 900) + 1
        for offset in range(cutoffs_total):
            cutoff = start + timedelta(minutes=15*offset)
            day = cutoff.strftime("%Y-%m-%d")
            overall["cutoffs_total"] += 1
            daily[day]["cutoffs_total"] += 1
            i, context = snapshot_choice(snapshot_times, cutoff)
            if i is None:
                overall[context] += 1
                daily[day][context] += 1
                continue
            snapshot = snapshots[i]
            selected = snapshot.members[:args.panel_size]
            overall["VALID_CONTEXT"] += 1
            daily[day]["valid_context"] += 1
            if len(selected) != args.panel_size:
                overall["INCOMPLETE_RECORDED_PANEL_CUTOFFS"] += 1
                daily[day]["incomplete_panel_cutoffs"] += 1
            for member in selected:
                sym = member.instrument.symbol
                overall["ranked_symbol_slots"] += 1
                daily[day]["ranked_slots"] += 1
                structural = True
                ingress = True
                for tf, n in REQUIRED.items():
                    opens, rows = series[(sym, tf)]
                    ok, failures, provenance = assess_window(
                        opens, rows, milliseconds(cutoff), tf, n,
                        args.settlement_seconds * 1000,
                    )
                    if not ok:
                        structural = False
                        for failure in failures:
                            reason_counts[f"{tf}:{failure}"] += 1
                    elif provenance != "INGEST_TIMESTAMPS_COMPATIBLE":
                        ingress = False
                        provenance_counts[f"{tf}:{provenance}"] += 1
                if structural:
                    overall["structural_pass_slots"] += 1
                    daily[day]["structural_pass_slots"] += 1
                    if ingress:
                        overall["ingestion_timestamp_compatible_slots"] += 1
                        daily[day]["ingestion_timestamp_compatible_slots"] += 1
                    else:
                        overall["structural_pass_but_late_or_unknown_ingestion_slots"] += 1
                        daily[day]["structural_pass_but_late_or_unknown_ingestion_slots"] += 1
                else:
                    overall["structural_fail_slots"] += 1
                    daily[day]["structural_fail_slots"] += 1
        conn.rollback()  # query-only transaction; never persist any mutations
    finally:
        conn.close()

    # Source-integrity errors invalidate admission even if descriptive counts
    # below remain useful diagnostics.
    outcome = "FAIL_CLOSED_ARCHIVE_INTEGRITY" if archive_errors else "RETROSPECTIVE_COVERAGE_RECORDED"
    report = {
        "schema_version": SCHEMA,
        "classification": "RECOVERY_RETROSPECTIVE",
        "status": outcome,
        "start": args.start,
        "end": args.end,
        "provider_id": PROVIDER,
        "panel_policy": f"FIRST_{args.panel_size}_RECORDED_RANKS_NO_SUBSTITUTION",
        "max_context_age_seconds": 300,
        "settlement_seconds_for_ingest_metadata": args.settlement_seconds,
        "depth_requirements": REQUIRED,
        "accepted_prospective_anchor": "2026-09-18T06:15:00Z",
        "admitted_new_prospective_families": 0,
        "prospective_ledger_written": False,
        "outcomes_evaluated": False,
        "holdout_opened": False,
        "production_action": False,
        "archive_files_inspected": archive_file_count,
        "valid_archive_snapshots_for_window": len(snapshots),
        "archive_content_manifest_sha256": manifest_hash.hexdigest(),
        "archive_integrity_error_count": len(archive_errors),
        "archive_integrity_error_sample": archive_errors,
        "selected_symbol_union_size": len(symbols),
        "closed_candle_rows_examined": source_rows,
        "current_db_candle_rows_sha256": source_rows_sha.hexdigest(),
        "counts": dict(sorted(overall.items())),
        "history_fail_reasons_by_tf": dict(sorted(reason_counts.items())),
        "ingestion_timing_warnings_by_tf": dict(sorted(provenance_counts.items())),
        "daily": {k:dict(sorted(v.items())) for k,v in sorted(daily.items())},
        "limitations": [
            "Historical current-state SQLite cannot independently prove that earlier versions of bars were never changed.",
            "ingested_at_ms is present-state metadata: compatibility is not proof of a historically immutable snapshot.",
            "This is coverage/causality diagnostic only. No strategy outcomes, candidate changes, prospective event counting or promotion.",
        ],
    }
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--start", default="2026-09-18T06:30:00Z")
    p.add_argument("--end", default="2026-09-25T10:15:00Z")
    p.add_argument("--research-root", default="/data/research")
    p.add_argument("--sqlite-db", default="/data/ktrader.db")
    p.add_argument("--panel-size", type=int, default=19)
    p.add_argument("--settlement-seconds", type=int, default=180)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return 0
    report = run(args)
    print(json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0 if report["archive_integrity_error_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
