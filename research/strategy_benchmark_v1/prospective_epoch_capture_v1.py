#!/usr/bin/env python3
"""Forward-only, server-local, DATA-ONLY Phase 11G prospective epoch recorder.

This does not evaluate strategies, touch the historic ledger, authorize trading,
or import K_AI/MT4. Output is an isolated first-seen record at future M15 cutoffs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
import urllib.request

PROVIDER = "binance_usdm"
DEPTHS = {"1d": 20, "4h": 80, "1h": 300, "15m": 400, "5m": 20}
STEP = {"1d": 86400000, "4h": 14400000, "1h": 3600000, "15m": 900000, "5m": 300000}
ROOT = Path("/data/research/phase11g/prospective_epochs")
SOURCE = Path("/data/research/universe/binance_usdm")
DATABASE = Path("/data/ktrader.db")
ANCHOR = Path("/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260918T061500Z.json")
OLD_LEDGER = Path("/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger/deduplicated_events.jsonl")
HARNESS = Path("/data/research/phase11g/strategy_benchmark_v1/harness/candidate_v2_2_backtest.py")
PROTOCOL = Path("/data/research/phase11g/strategy_benchmark_v1/protocol.json")
HARNESS_SHA = "b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08"
PROTOCOL_SHA = "ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3"


def hbytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def utc(value):
    v = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if v.tzinfo is None or v.utcoffset() != timedelta(0):
        raise ValueError("UTC timezone required")
    return v.astimezone(timezone.utc)


def tag(t):
    return t.strftime("%Y%m%dT%H%M%SZ")


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def mill(t):
    return int(t.timestamp() * 1000)


def filename_time(name):
    return datetime.strptime(name.split("_", 1)[0], "%Y%m%dT%H%M%S%fZ").replace(tzinfo=timezone.utc)


def next_closed_start(now):
    t = now.replace(second=0, microsecond=0)
    return (t.replace(minute=t.minute // 15 * 15) + timedelta(minutes=30))


def latest_snapshot_file(cutoff, source=SOURCE):
    days = {cutoff.date(), (cutoff - timedelta(minutes=10)).date()}
    choices = []
    for d in days:
        directory = source / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.day:02d}"
        for file in directory.glob("*.jsonl") if directory.is_dir() else []:
            try:
                when = filename_time(file.name)
            except ValueError:
                continue
            age = (cutoff - when).total_seconds()
            if 0 <= age <= 600:
                choices.append((when, file))
    if not choices:
        return None, None, "MISSING_CONTEXT"
    when, file = max(choices)
    age = (cutoff - when).total_seconds()
    if age > 300:
        return file, age, "STALE_CONTEXT"
    return file, age, "VALID_CONTEXT"


def verify_archive(path, cutoff, expected_config):
    from ktrader.history.universe import load_universe_archive

    record = load_universe_archive(path)  # canonical digests/ranks/config check
    if record.provider_id != PROVIDER or len(record.snapshots) != 1:
        raise ValueError("provider mismatch or non-singleton source archive")
    snapshot = record.snapshots[0]
    if snapshot.captured_at != filename_time(path.name):
        raise ValueError("archive filename timestamp mismatch")
    if snapshot.captured_at > cutoff or (cutoff - snapshot.captured_at).total_seconds() > 300:
        raise ValueError("future/stale snapshot")
    first = json.loads(path.open(encoding="utf-8").readline())
    if first.get("config") != expected_config:
        raise ValueError("universe configuration drift")
    return snapshot, sha_file(path), first


def bar_window(rows, tf, cutoff_ms, depth, settle_ms):
    step = STEP[tf]
    last_open = (cutoff_ms // step - 1) * step
    selected = [x for x in rows if x["open_time_ms"] <= last_open]
    selected = selected[-depth:]
    failures = []
    if len(selected) != depth:
        failures.append("INSUFFICIENT_DEPTH")
    if not selected or selected[-1]["open_time_ms"] != last_open:
        failures.append("MISSING_LAST_CLOSED_BAR")
    if any(x["close_time_ms"] != x["open_time_ms"] + step - 1 for x in selected):
        failures.append("INVALID_CLOSE")
    if any(b["open_time_ms"] - a["open_time_ms"] != step for a, b in zip(selected, selected[1:])):
        failures.append("HISTORY_GAP")
    if any(x["close_time_ms"] >= cutoff_ms or not x["closed"] for x in selected):
        failures.append("LOOKAHEAD_OR_UNCLOSED")
    ingest_ready = bool(selected) and all(
        isinstance(x["ingested_at_ms"], int) and 0 < x["ingested_at_ms"] <= cutoff_ms + settle_ms
        for x in selected
    )
    if not ingest_ready:
        failures.append("LATE_OR_UNKNOWN_INGESTION")
    return selected, failures


def fetch_window(db, symbol, tf, cutoff_ms):
    # Indexed read, one consistent read-only transaction for the entire cutoff.
    step = STEP[tf]
    last_open = (cutoff_ms // step - 1) * step
    rows = db.execute(
        "SELECT open_time_ms,close_time_ms,open_price,high_price,low_price,close_price,"
        "volume,quote_volume,trade_count,taker_buy_volume,taker_buy_quote_volume,"
        "closed,ingested_at_ms,source_kind,derived_from_interval "
        "FROM candles WHERE provider_id=? AND symbol=? AND interval=? AND open_time_ms<=? "
        "AND closed=1 ORDER BY open_time_ms DESC LIMIT ?",
        (PROVIDER, symbol, tf, last_open, DEPTHS[tf]),
    ).fetchall()
    names = ("open_time_ms", "close_time_ms", "open", "high", "low", "close", "volume",
             "quote_volume", "trade_count", "taker_buy_volume", "taker_buy_quote_volume",
             "closed", "ingested_at_ms", "source_kind", "derived_from_interval")
    return [dict(zip(names, row)) for row in reversed(rows)]


def immutable_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as f:
        f.write(canonical(value) + "\n")
        f.flush()
        os.fsync(f.fileno())
    path.chmod(0o400)


def append_event(root, event):
    # Mutable status/event log is separate from immutable per-cutoff data.
    with (root / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(canonical(event) + "\n")
        f.flush()
        os.fsync(f.fileno())


def validate_registration(regpath, scriptpath, check_future=False):
    r = json.loads(regpath.read_text())
    required = {
        "schema_version": "ktrader.phase11g.prospective_epoch.registration.v1",
        "classification": "FORWARD_FIRST_SEEN_DATA_ONLY",
        "provider_id": PROVIDER,
        "panel_rule": "FIRST_19_RECORDED_RANKS_NO_SUBSTITUTION",
        "panel_size": 19,
        "settle_seconds": 180,
        "max_capture_delay_seconds": 300,
        "original_resolved_families": 54,
        "old_harness_sha256": HARNESS_SHA,
        "old_protocol_sha256": PROTOCOL_SHA,
        "strategy_evaluation_enabled": False,
        "trading_authorized": False,
        "holdout_opened": False,
        "hp_omen_allowed": False,
        "admitted_new_prospective_families": 0,
    }
    for key, wanted in required.items():
        if r.get(key) != wanted:
            raise ValueError("registration contract mismatch: " + key)
    start, end, registered = (utc(r[k]) for k in ("start_cutoff_utc", "end_cutoff_utc", "registered_at_utc"))
    if (start.second or start.microsecond or start.minute % 15 or end.second or end.microsecond or end.minute % 15):
        raise ValueError("start/end not M15 boundaries")
    if not (end >= start > registered + timedelta(minutes=15)):
        raise ValueError("registration is not strictly future-looking")
    if check_future and datetime.now(timezone.utc) > start:
        raise ValueError("registration start has already passed")
    if regpath.parent.parent != ROOT or regpath.parent.name != r.get("epoch_id"):
        raise ValueError("epoch path not in isolated canonical namespace")
    pinned = {
        "recorder_sha256": sha_file(scriptpath),
        "old_anchor_sha256": sha_file(ANCHOR),
        "old_ledger_sha256": sha_file(OLD_LEDGER),
        "old_harness_sha256": sha_file(HARNESS),
        "old_protocol_sha256": sha_file(PROTOCOL),
    }
    for key, actual in pinned.items():
        if r.get(key) != actual:
            raise ValueError("pinned source changed: " + key)
    if json.loads(ANCHOR.read_text()).get("resolved_primary_families") != 54:
        raise ValueError("accepted immutable anchor count changed")
    if "HP-OMEN" in str(regpath) or "K_AI" in str(regpath):
        raise ValueError("wrong host/project storage")
    return r, start, end


def health():
    with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=5) as resp:
        v = json.load(resp)
    if v.get("mode") != "read_only" or v.get("data_ready") is not True:
        raise RuntimeError("production health governance invariant failed")
    if v.get("provider_id") != PROVIDER:
        raise RuntimeError("production market data provider mismatch")
    return {"status": v.get("status"), "mode": v["mode"], "provider_id": v["provider_id"]}


def capture(reg, cutoff, root, scriptpath):
    # Safety first: no previous-epoch ledger mutation or retroactive capture.
    validate_registration(root / "registration.json", scriptpath)
    age = (datetime.now(timezone.utc) - cutoff).total_seconds()
    if age < reg["settle_seconds"] or age > reg["max_capture_delay_seconds"]:
        raise RuntimeError("cutoff outside approved first-seen capture timing")
    live_health = health()
    source, context_age, selection = latest_snapshot_file(cutoff)
    final = root / "cutoffs" / tag(cutoff)
    staging = root / "cutoffs" / ("_inflight_" + tag(cutoff))
    if final.exists() or staging.exists():
        raise FileExistsError("immutable cutoff output collision")
    staging.mkdir(mode=0o700)
    result = {
        "schema_version": "ktrader.phase11g.prospective_epoch.capture.v1",
        "classification": "FORWARD_FIRST_SEEN_DATA_ONLY",
        "epoch_id": reg["epoch_id"],
        "cutoff_utc": iso(cutoff),
        "first_seen_recorded_at_utc": iso(datetime.now(timezone.utc)),
        "health": live_health,
        "context_status": selection,
        "context_age_seconds": context_age,
        "recorded_ranked_panel_size": 0,
        "full_depth_ready_slots": 0,
        "first_seen_ingestion_compatible_slots": 0,
        "failed_slots": 0,
        "source_files": {},
        "symbol_statuses": [],
        "strategy_evaluated": False,
        "admitted_new_prospective_families": 0,
        "holdout_opened": False,
        "production_action": False,
    }
    if selection == "VALID_CONTEXT":
        snapshot, archive_sha, _ = verify_archive(source, cutoff, reg["universe_config"])
        result["universe_archive_path"] = source.as_posix()
        result["universe_archive_sha256"] = archive_sha
        result["universe_captured_at_utc"] = iso(snapshot.captured_at)
        # If the archive was only written after the approved capture window,
        # do not represent it as timely contemporary context.
        if source.stat().st_mtime > cutoff.timestamp() + reg["max_capture_delay_seconds"]:
            raise RuntimeError("universe source file was published too late")
        members = snapshot.members[:reg["panel_size"]]
        result["recorded_ranked_panel_size"] = len(members)
        if len(members) < reg["panel_size"]:
            result["context_status"] = "INCOMPLETE_RECORDED_PANEL"
        if members:
            conn = sqlite3.connect("file:/data/ktrader.db?mode=ro", uri=True, timeout=5)
            conn.execute("PRAGMA query_only=ON")
            conn.execute("BEGIN")
            try:
                for m in members:
                    symbol = m.instrument.symbol
                    row = {"rank": m.rank, "symbol": symbol, "timeframes": {}, "structurally_ready": True,
                           "ingestion_compatible": True, "failed": False}
                    for tf, depth in DEPTHS.items():
                        bars = fetch_window(conn, symbol, tf, mill(cutoff))
                        checked, failures = bar_window(bars, tf, mill(cutoff), depth, reg["settle_seconds"] * 1000)
                        info = {"count": len(checked), "required": depth, "failures": failures}
                        if failures:
                            row["failed"] = True
                        if any(f != "LATE_OR_UNKNOWN_INGESTION" for f in failures):
                            row["structurally_ready"] = False
                        if "LATE_OR_UNKNOWN_INGESTION" in failures:
                            row["ingestion_compatible"] = False
                        # Persist exact as-first-seen data, including explicit
                        # ingestion timestamps, for independent future analysis.
                        path = staging / "candles" / symbol
                        path.mkdir(parents=True, exist_ok=True)
                        file = path / (tf + ".jsonl")
                        with file.open("x", encoding="utf-8", newline="\n") as f:
                            for bar in checked:
                                f.write(canonical(bar) + "\n")
                            f.flush()
                            os.fsync(f.fileno())
                        file.chmod(0o400)
                        rel = file.relative_to(staging).as_posix()
                        result["source_files"][rel] = sha_file(file)
                        info["file_sha256"] = result["source_files"][rel]
                        row["timeframes"][tf] = info
                    result["symbol_statuses"].append(row)
                    if row["structurally_ready"]:
                        result["full_depth_ready_slots"] += 1
                    if row["structurally_ready"] and row["ingestion_compatible"]:
                        result["first_seen_ingestion_compatible_slots"] += 1
                    if row["failed"]:
                        result["failed_slots"] += 1
            finally:
                conn.rollback()
                conn.close()
    result["completed_at_utc"] = iso(datetime.now(timezone.utc))
    if (datetime.now(timezone.utc) - cutoff).total_seconds() > reg["max_capture_delay_seconds"]:
        raise RuntimeError("capture exceeded accepted first-seen delay")
    immutable_json(staging / "manifest.json", result)
    staging.rename(final)
    os.chmod(final, 0o500)
    return result


def self_test():
    base = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
    assert (base - filename_time("20260925T115539000000Z_demo.jsonl")).total_seconds() <= 300
    assert latest_snapshot_file(base, Path("/nonexistent"))[2] == "MISSING_CONTEXT"
    assert next_closed_start(base + timedelta(minutes=1)) > base + timedelta(minutes=15)
    cutoff = mill(base + timedelta(minutes=15))
    h = STEP["1h"]
    hourly = [
        {"open_time_ms": i*h, "close_time_ms": (i+1)*h-1, "closed": 1, "ingested_at_ms": (i+1)*h+1000}
        for i in range(cutoff//h - 3, cutoff//h + 1)
    ]
    checked, failures = bar_window(hourly, "1h", cutoff, 3, 180000)
    assert len(checked) == 3 and checked[-1]["open_time_ms"] == (cutoff//h-1)*h
    assert not failures
    late = [dict(x) for x in hourly]
    late[-2]["ingested_at_ms"] = cutoff + 180001
    assert "LATE_OR_UNKNOWN_INGESTION" in bar_window(late, "1h", cutoff, 3, 180000)[1]
    missing = [x for x in hourly if x["open_time_ms"] != (cutoff//h-2)*h]
    assert "HISTORY_GAP" in bar_window(missing, "1h", cutoff, 3, 180000)[1] or "INSUFFICIENT_DEPTH" in bar_window(missing, "1h", cutoff, 3, 180000)[1]
    print("SELF_TEST=PASS (6 gates)")


def runner(regpath, scriptpath, once=False):
    reg, start, end = validate_registration(regpath, scriptpath, check_future=True)
    root = regpath.parent
    lock = (root / "runner.lock").open("x")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    cutoffs = root / "cutoffs"
    cutoffs.mkdir(exist_ok=False)
    append_event(root, {"event": "REGISTERED_RUNNER_START", "recorded_at_utc": iso(datetime.now(timezone.utc)),
                        "first_cutoff": iso(start), "last_cutoff": iso(end)})
    current = start
    try:
        while current <= end:
            goal = current + timedelta(seconds=reg["settle_seconds"])
            delay = (goal - datetime.now(timezone.utc)).total_seconds()
            if delay > 0:
                print("WAITING", iso(current), "seconds", round(delay, 2), flush=True)
                time.sleep(delay)
            print("CAPTURING", iso(current), flush=True)
            outcome = capture(reg, current, root, scriptpath)
            status = {"status": "PASS", "latest_cutoff": iso(current),
                      "full_depth_ready_slots": outcome["full_depth_ready_slots"],
                      "first_seen_ingestion_compatible_slots": outcome["first_seen_ingestion_compatible_slots"],
                      "failed_slots": outcome["failed_slots"], "admitted_new_prospective_families": 0}
            (root / "status.json").write_text(canonical(status) + "\n")
            append_event(root, {"event": "FIRST_SEEN_CAPTURE", "cutoff": iso(current),
                                "manifest_sha256": sha_file(cutoffs / tag(current) / "manifest.json"),
                                **status})
            print(canonical(status), flush=True)
            if once:
                return 0
            current += timedelta(minutes=15)
        (root / "status.json").write_text(canonical({"status": "COMPLETE_BOUNDARY", "last_cutoff": iso(end)}) + "\n")
        return 0
    except Exception as exc:
        fail = {"status": "FAIL_CLOSED", "at_cutoff": iso(current), "error_type": type(exc).__name__,
                "error": str(exc)[:300], "admitted_new_prospective_families": 0}
        (root / "status.json").write_text(canonical(fail) + "\n")
        append_event(root, {"event": "FAIL_CLOSED", **fail})
        print(canonical(fail), file=sys.stderr, flush=True)
        return 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--registration", type=Path)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.registration or (args.preflight == args.run):
        parser.error("exactly one of --preflight and --run, plus --registration, is required")
    reg, start, end = validate_registration(args.registration, Path(__file__), check_future=True)
    if args.preflight:
        live = health()
        print(canonical({"status": "PASS", "epoch_id": reg["epoch_id"], "start": iso(start),
                         "until": iso(end), "health": live, "recording_only": True,
                         "admitted_new_prospective_families": 0}))
        return 0
    return runner(args.registration, Path(__file__), once=args.once)


if __name__ == "__main__":
    raise SystemExit(main())
