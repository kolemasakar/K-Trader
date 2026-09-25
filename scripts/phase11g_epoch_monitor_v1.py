#!/usr/bin/env python3
"""Bounded, local-only monitoring of the approved Phase 11G data-only epoch.

Checks are journaled to server storage; there are NO messages or reminders.
The monitor NEVER starts, restarts, changes, or backfills the capture process.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request

UTC = timezone.utc
EPOCH = Path("/data/research/phase11g/prospective_epochs/epoch_20260925T114500Z_v1")
BASE = Path("/data/research/phase11g/strategy_benchmark_v1")
FIRST = datetime(2026, 9, 25, 11, 45, tzinfo=UTC)
LAST = datetime(2026, 9, 26, 11, 30, tzinfo=UTC)
START_HOURLY = datetime(2026, 9, 25, 12, 6, tzinfo=UTC)
START_DEEP = datetime(2026, 9, 25, 15, 51, tzinfo=UTC)
FINAL = datetime(2026, 9, 26, 11, 36, tzinfo=UTC)
EXPECTED_REG_SHA = "b67a2d4c587995d4b58649ea136e99306dfe5927a178565cc176b82f36b7ef9e"
EXPECTED_RECORDER_SHA = "3ff7d5ff85f315e785fb5eca8b28ef04fc6fa150374c85edfd0db10b67465213"
EXPECTED_ANCHOR_SHA = "30d0510da10d3d8b40684f8bf97c9ae568a6b3b8a7b43289c6b8cd41543a997b"
EXPECTED_LEDGER_SHA = "c0c1b261a6684d1f9381e820736f9dd702319947e3e7f78fb38b607508dcfade"
EXPECTED_HARNESS_SHA = "b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08"
EXPECTED_PROTOCOL_SHA = "ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3"


def iso(t: datetime) -> str:
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def tag(t: datetime) -> str:
    return t.strftime("%Y%m%dT%H%M%SZ")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def schedule() -> list[tuple[datetime, str]]:
    items = []
    t = START_HOURLY
    while t <= FINAL:
        items.append((t, "HOURLY"))
        t += timedelta(hours=1)
    t = START_DEEP
    while t < FINAL:
        items.append((t, "DEEP"))
        t += timedelta(hours=4)
    items.append((FINAL, "FINAL"))
    return sorted(items, key=lambda x: (x[0], x[1]))


def expected_cutoffs(now: datetime) -> list[datetime]:
    # Check only after the entire first-seen capture deadline has elapsed.
    t = FIRST
    result = []
    while t <= LAST and t + timedelta(minutes=5) <= now:
        result.append(t)
        t += timedelta(minutes=15)
    return result


def exact_runner_pids() -> list[int]:
    found = []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            args = (p / "cmdline").read_bytes().split(b"\0")
            if (len(args) > 2 and args[1].endswith(b"/prospective_epoch_capture_v1.py")
                    and b"--run" in args and b"--registration" in args):
                found.append(int(p.name))
        except (OSError, PermissionError):
            pass
    return sorted(found)


def frozen_pins(root: Path = EPOCH, base: Path = BASE) -> dict[str, bool]:
    paths = {
        "registration": (root / "registration.json", EXPECTED_REG_SHA),
        "recorder": (root / "prospective_epoch_capture_v1.py", EXPECTED_RECORDER_SHA),
        "accepted_state": (base / "combined_rules/current_state_manifests/20260918T061500Z.json", EXPECTED_ANCHOR_SHA),
        "original_ledger": (base / "combined_rules/prospective_v2_2_ledger/deduplicated_events.jsonl", EXPECTED_LEDGER_SHA),
        "frozen_harness": (base / "harness/candidate_v2_2_backtest.py", EXPECTED_HARNESS_SHA),
        "frozen_protocol": (base / "protocol.json", EXPECTED_PROTOCOL_SHA),
    }
    return {name: path.is_file() and sha(path) == digest for name, (path, digest) in paths.items()}


def get_health() -> dict:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=5) as stream:
            data = json.load(stream)
        return {
            "status": data.get("status"),
            "mode": data.get("mode"),
            "provider": data.get("provider_id"),
            "data_ready": data.get("data_ready"),
        }
    except Exception as error:
        return {"error_type": type(error).__name__}


def inspect_cutoff(root: Path, cutoff: datetime, deep: bool,
                   events_by_cutoff: dict[str, str]) -> dict:
    name = tag(cutoff)
    d = root / "cutoffs" / name
    output = {"cutoff_utc": iso(cutoff), "status": "PASS"}
    file = d / "manifest.json"
    failures = []
    if not file.is_file():
        output["status"] = "FAIL_CLOSED"
        output["failures"] = ["MISSING_IMMUTABLE_MANIFEST"]
        output["inflight_exists"] = (root / "cutoffs" / ("_inflight_" + name)).exists()
        return output
    try:
        m = json.loads(file.read_text(encoding="utf-8"))
        digest = sha(file)
        if events_by_cutoff.get(iso(cutoff)) != digest:
            failures.append("EVENT_MANIFEST_HASH_MISMATCH")
        if m.get("classification") != "FORWARD_FIRST_SEEN_DATA_ONLY" or m.get("epoch_id") != root.name:
            failures.append("EPOCH_IDENTITY_OR_CLASSIFICATION")
        if m.get("cutoff_utc") != iso(cutoff):
            failures.append("INCORRECT_CUTOFF")
        if any(m.get(k) is not False for k in ("holdout_opened", "production_action", "strategy_evaluated")):
            failures.append("GOVERNANCE_FLAGS")
        if m.get("admitted_new_prospective_families") != 0:
            failures.append("UNAUTHORIZED_FAMILY_COUNT")
        for key in ("first_seen_recorded_at_utc", "completed_at_utc"):
            when = parse(m[key])
            if not cutoff + timedelta(minutes=3) <= when <= cutoff + timedelta(minutes=5):
                failures.append("OUT_OF_BOUNDS_" + key.upper())
        count = m.get("recorded_ranked_panel_size")
        statuses = m.get("symbol_statuses", [])
        if count != 19 or len(statuses) != 19 or [row.get("rank") for row in statuses] != list(range(1, 20)):
            failures.append("MISSING_OR_SUBSTITUTED_RANKS")
        paths = m.get("source_files", {})
        if count == 19 and len(paths) != 95:
            failures.append("SOURCE_FILE_COUNT")
        output.update({"manifest_sha256": digest, "raw_file_count": len(paths),
                       "ready_slots": m.get("full_depth_ready_slots"),
                       "ingestion_compatible_slots": m.get("first_seen_ingestion_compatible_slots"),
                       "failed_slots": m.get("failed_slots"),
                       "context_status": m.get("context_status")})
        if m.get("context_status") != "VALID_CONTEXT":
            failures.append("CONTEXT_NOT_VALID")
        if deep:
            raw_fail = []
            for rel, expected in paths.items():
                p = d / rel
                if not p.is_file() or sha(p) != expected:
                    raw_fail.append(rel)
            output["raw_sha_verified"] = len(paths) - len(raw_fail)
            if raw_fail:
                failures.append("RAW_SHA_MISMATCH")
                output["failed_raw_files"] = raw_fail[:5]
            source = Path(m.get("universe_archive_path") or "")
            if not source.is_file() or sha(source) != m.get("universe_archive_sha256"):
                failures.append("ARCHIVE_HASH_MISMATCH")
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        failures.append("BAD_MANIFEST_" + type(exc).__name__)
    if failures:
        output.update({"status": "FAIL_CLOSED", "failures": failures})
    return output


def review(root: Path, due: datetime, kind: str, now: datetime | None = None) -> dict:
    now = now or datetime.now(UTC)
    required = expected_cutoffs(due)
    full = kind in ("DEEP", "FINAL")
    paths = frozen_pins(root)
    health = get_health()
    runner = exact_runner_pids()
    issues = []
    if not all(paths.values()):
        issues.append("IMMUTABLE_PIN_DRIFT")
    if health.get("mode") != "read_only" or health.get("provider") != "binance_usdm":
        issues.append("SERVER_READONLY_OR_PROVIDER_FAILURE")
    if kind != "FINAL" and len(runner) != 1:
        issues.append("RUNNER_COUNT_NOT_ONE")
    if kind == "FINAL" and runner:
        issues.append("RUNNER_STILL_RUNNING_AFTER_BOUNDARY")
    events_by_cutoff = {}
    try:
        lines = (root / "events.jsonl").read_text().splitlines()
        events = [json.loads(line) for line in lines if line.strip()]
        starts = [v for v in events if v.get("event") == "REGISTERED_RUNNER_START"]
        if len(starts) != 1 or starts[0].get("first_cutoff") != iso(FIRST):
            issues.append("STARTUP_EVENT_COUNT_OR_BOUNDARY")
        for event in events:
            if event.get("event") == "FIRST_SEEN_CAPTURE":
                key = event.get("cutoff")
                if key in events_by_cutoff:
                    issues.append("DUPLICATE_FIRST_SEEN_EVENT")
                events_by_cutoff[key] = event.get("manifest_sha256")
            if event.get("event") == "FAIL_CLOSED":
                issues.append("RUNNER_FAIL_CLOSED_EVENT")
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        issues.append("EVENT_LOG_INVALID")
    if kind == "FINAL":
        try:
            s = json.loads((root / "status.json").read_text())
            if s.get("status") != "COMPLETE_BOUNDARY":
                issues.append("NOT_COMPLETE_BOUNDARY")
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            issues.append("FINAL_STATUS_INVALID")
    all_out = []
    recent = set(required[-4:])
    for cutoff in required:
        # Every check verifies continuity/manifest identity; deep/final audit ALL SHA.
        result = inspect_cutoff(root, cutoff, deep=full or cutoff in recent, events_by_cutoff=events_by_cutoff)
        all_out.append(result)
    bad = [x for x in all_out if x["status"] != "PASS"]
    if bad:
        issues.append("CUTOFF_AUDIT_FAILURE")
    report = {
        "schema_version": "ktrader.phase11g.epoch_monitor.v1",
        "classification": "AUTOMATED_MONITOR_NO_REMINDERS",
        "kind": kind,
        "scheduled_utc": iso(due),
        "observed_at_utc": iso(now),
        "monitor_delay_seconds": max(0, int((now-due).total_seconds())),
        "expected_cutoffs": len(required),
        "pass_cutoffs": len(all_out)-len(bad),
        "failed_cutoffs": len(bad),
        "raw_files_hashed": sum(x.get("raw_sha_verified", 0) for x in all_out),
        "first_seen_event_count": len(events_by_cutoff),
        "exact_recorder_pids": runner,
        "frozen_pins": paths,
        "health": health,
        "ready_slots_last": all_out[-1].get("ready_slots") if all_out else None,
        "failed_slots_last": all_out[-1].get("failed_slots") if all_out else None,
        "failure_reasons": sorted(set(issues)),
        "failed_cutoffs_sample": bad[:8],
        "status": "PASS" if not issues else "FAIL_CLOSED",
        "prospective_families_admitted": 0,
        "notifications_scheduled": False,
        "trading_authorized": False,
    }
    return report


def immutable_report(out: Path, report: dict) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as f:
        f.write(json.dumps(report, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def log(outroot: Path, report: dict) -> None:
    with (outroot / "checks.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(report, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def self_test() -> None:
    s = schedule()
    assert len([x for x in s if x[1] == "HOURLY"]) == 24
    assert len([x for x in s if x[1] == "DEEP"]) == 5
    assert len([x for x in s if x[1] == "FINAL"]) == 1
    assert s[0] == (START_HOURLY, "HOURLY")
    assert s[-1] == (FINAL, "FINAL")
    assert len(expected_cutoffs(datetime(2026, 9, 25, 12, 6, tzinfo=UTC))) == 2
    assert len(expected_cutoffs(FINAL)) == 96
    assert expected_cutoffs(datetime(2026, 9, 25, 11, 49, tzinfo=UTC)) == []
    print("EPOCH_MONITOR_SELF_TEST=PASS (8 checks)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--baseline", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not (args.run or args.baseline) or (args.run and args.baseline):
        ap.error("choose exactly one of --run or --baseline")
    reg = EPOCH / "registration.json"
    if not reg.is_file() or sha(reg) != EXPECTED_REG_SHA:
        raise SystemExit("FAIL_CLOSED: missing or changed approved registration")
    if not all(frozen_pins(EPOCH).values()):
        raise SystemExit("FAIL_CLOSED: preregistered identity changed")
    if args.baseline:
        print(json.dumps(review(EPOCH, datetime.now(UTC), "BASELINE"), sort_keys=True))
        return 0
    out = EPOCH / "checks"
    out.mkdir(mode=0o700, exist_ok=False)
    lockpath = out / "monitor.lock"
    lock = lockpath.open("x")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    now = datetime.now(UTC)
    baseline = review(EPOCH, now, "BASELINE", now)
    immutable_report(out / "baseline.json", baseline)
    log(out, baseline)
    for due, kind in schedule():
        now = datetime.now(UTC)
        if due < now:
            report = {
                "kind": kind,
                "scheduled_utc": iso(due),
                "observed_at_utc": iso(now),
                "status": "MISSED_BEFORE_MONITOR_ACTIVATION",
                "notifications_scheduled": False,
            }
        else:
            time.sleep(max(0, (due-now).total_seconds()))
            observed = datetime.now(UTC)
            report = review(EPOCH, due, kind, observed)
        fname = f"{tag(due)}_{kind.lower()}.json"
        immutable_report(out / fname, report)
        log(out, report)
        print(json.dumps({k: report.get(k) for k in (
            "kind", "status", "scheduled_utc", "observed_at_utc",
            "expected_cutoffs", "failed_cutoffs", "failure_reasons")}, sort_keys=True), flush=True)
    print("EPOCH_MONITOR_COMPLETE", iso(datetime.now(UTC)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
