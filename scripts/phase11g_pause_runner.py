#!/usr/bin/env python3
"""Data-only Phase 11G M15 automation for a bounded pause window.

This runner is deliberately narrow: it can only advance the accepted research
pipeline sequentially, verify read-only/holdout invariants, and emit diagnostics.
It never changes candidate_rule_set_v2_2, opens holdout, activates Phase 12,
selects production risk, or authorizes trading.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

FROZEN_STRATEGY = "candidate_rule_set_v2_2"
RESOLVER = "v1.3"
DEFAULT_BASE = Path("/data/research/phase11g/strategy_benchmark_v1/combined_rules")


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def tag(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def floor_m15(dt: datetime) -> datetime:
    dt = dt.astimezone(timezone.utc).replace(second=0, microsecond=0)
    return dt.replace(minute=(dt.minute // 15) * 15)


def accepted_state(path: Path) -> dict | None:
    try:
        state = json.loads(path.read_text())
    except Exception:
        return None
    if state.get("status") != "PASS":
        return None
    if state.get("strategy_id") != FROZEN_STRATEGY or state.get("resolver_version") != RESOLVER:
        return None
    if state.get("holdout_opened") is not False or state.get("production_action") is not False:
        return None
    if state.get("unique_families") != state.get("resolved_primary_families", 0) + state.get("unresolved_primary_families", 0):
        return None
    return state


def latest_accepted(state_dir: Path) -> tuple[Path, dict]:
    for path in sorted(state_dir.glob("*.json"), reverse=True):
        state = accepted_state(path)
        if state is not None:
            return path, state
    raise RuntimeError("no accepted state manifest")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_manifest(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text())
    root = Path(manifest["root"])
    failures = []
    for rel, expected in sorted(manifest["files"].items()):
        p = root / rel
        if not p.is_file():
            failures.append(f"missing:{rel}")
        elif sha256(p) != expected:
            failures.append(f"sha256:{rel}")
    if failures:
        raise RuntimeError("runtime manifest mismatch: " + ",".join(failures))


def health_check(url: str) -> tuple[str, dict | None]:
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            body = json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        return "UNAVAILABLE", {"error": str(exc)}
    if body.get("mode") != "read_only":
        return "GOVERNANCE_BLOCKER", body
    if body.get("data_ready") is not True:
        return "DATA_NOT_READY", body
    return "PASS", body


def run_checked(cmd: list[str], stdout_path: Path) -> None:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("a", encoding="utf-8") as out:
        p = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, text=True)
    if p.returncode:
        raise RuntimeError(f"command failed rc={p.returncode}: {' '.join(cmd)}")


def append_event(log_path: Path, event: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    event = {"recorded_at": iso_z(datetime.now(timezone.utc)), **event}
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")


def write_status(path: Path, status: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def build_pipeline_command(runtime_dir: Path, cutoff: datetime, prior: Path, prereg_boundary: str) -> list[str]:
    return [
        sys.executable,
        str(runtime_dir / "run_prospective_research_pipeline_v2.py"),
        "--as-of", iso_z(cutoff),
        "--prior-outcomes", str(prior),
        "--script-dir", str(runtime_dir),
        "--prereg-boundary", prereg_boundary,
        "--execute",
    ]


def post_cycle_checks(base: Path, tools_dir: Path, cutoff: datetime, run_root: Path, outcomes: Path, checks_root: Path) -> None:
    t = tag(cutoff)
    out = checks_root / t
    state = base / "current_state_manifests" / f"{t}.json"
    families = outcomes / "families.jsonl"
    bundle_root = run_root / "bundles"
    run_checked([sys.executable, str(tools_dir / "phase11g_guardrails.py"), str(state), "--output", str(out / "guardrails.json")], out / "guardrails.log")
    run_checked([sys.executable, str(tools_dir / "phase11g_data_quality_watchdog.py"), str(bundle_root), "--as-of", iso_z(cutoff), "--output", str(out / "data_quality.json")], out / "data_quality.log")
    if families.is_file():
        run_checked([sys.executable, str(tools_dir / "phase11g_path_quality.py"), str(families), "--as-of", iso_z(cutoff), "--output", str(out / "path_quality.json")], out / "path_quality.log")


def run_iteration(a: argparse.Namespace) -> dict:
    verify_manifest(a.runtime_manifest)
    verify_manifest(a.tools_manifest)
    health_status, health = health_check(a.health_url)
    if health_status == "GOVERNANCE_BLOCKER":
        raise RuntimeError("production mode is not read_only")
    if health_status != "PASS":
        return {"status": "SKIP_HEALTH", "health_status": health_status, "health": health}

    state_path, state = latest_accepted(a.base / "current_state_manifests")
    current = parse_utc(state["as_of"])
    now = datetime.now(timezone.utc)
    target = floor_m15(now - timedelta(seconds=a.settle_seconds))
    if target >= a.until:
        target = floor_m15(a.until - timedelta(seconds=1))
    advanced = []

    while current + timedelta(minutes=15) <= target:
        cutoff = current + timedelta(minutes=15)
        prior_tag = tag(current)
        cutoff_tag = tag(cutoff)
        prior = a.base / "prospective_v2_2_outcomes_offline_v1_3" / prior_tag
        if not prior.is_dir():
            raise RuntimeError(f"missing prior outcomes {prior}")
        run_root = Path("/data/research/phase11g") / f"v2_2_shadow_{cutoff_tag}"
        outcomes = a.base / "prospective_v2_2_outcomes_offline_v1_3" / cutoff_tag
        pipeline_log = a.automation_root / "pipeline_logs" / f"{cutoff_tag}.log"
        run_checked(build_pipeline_command(a.runtime_dir, cutoff, prior, a.prereg_boundary), pipeline_log)
        new_state_path = a.base / "current_state_manifests" / f"{cutoff_tag}.json"
        new_state = accepted_state(new_state_path)
        if new_state is None:
            raise RuntimeError(f"new state did not pass invariants: {new_state_path}")
        post_cycle_checks(a.base, a.tools_dir, cutoff, run_root, outcomes, a.automation_root / "checks")
        advanced.append({
            "cutoff": iso_z(cutoff),
            "state_sha256": sha256(new_state_path),
            "resolved": new_state.get("resolved_primary_families"),
            "unresolved": new_state.get("unresolved_primary_families"),
            "unique": new_state.get("unique_families"),
        })
        current = cutoff
        state_path, state = new_state_path, new_state

    return {
        "status": "PASS",
        "latest_as_of": state.get("as_of"),
        "latest_state": str(state_path),
        "latest_state_sha256": sha256(state_path),
        "resolved": state.get("resolved_primary_families"),
        "unresolved": state.get("unresolved_primary_families"),
        "unique": state.get("unique_families"),
        "advanced": advanced,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, default=DEFAULT_BASE)
    ap.add_argument("--runtime-dir", type=Path, required=True)
    ap.add_argument("--runtime-manifest", type=Path, required=True)
    ap.add_argument("--tools-dir", type=Path, required=True)
    ap.add_argument("--tools-manifest", type=Path, required=True)
    ap.add_argument("--automation-root", type=Path, required=True)
    ap.add_argument("--not-before", type=parse_utc, required=True)
    ap.add_argument("--until", type=parse_utc, required=True)
    ap.add_argument("--prereg-boundary", default="2026-09-16T13:00:00Z")
    ap.add_argument("--settle-seconds", type=int, default=180)
    ap.add_argument("--poll-seconds", type=int, default=60)
    ap.add_argument("--health-url", default="http://127.0.0.1:8000/health")
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args()

    if a.not_before >= a.until:
        raise SystemExit("not-before must be before until")
    a.automation_root.mkdir(parents=True, exist_ok=True)
    lock_path = a.automation_root / "runner.lock"
    lock = lock_path.open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"status": "ALREADY_RUNNING"}))
        return 0

    events = a.automation_root / "events.jsonl"
    status_path = a.automation_root / "status.json"
    append_event(events, {"event": "RUNNER_START", "not_before": iso_z(a.not_before), "until": iso_z(a.until)})

    while True:
        now = datetime.now(timezone.utc)
        if now >= a.until:
            final = {"status": "STOPPED_AT_BOUNDARY", "stopped_at": iso_z(now), "until": iso_z(a.until)}
            write_status(status_path, final); append_event(events, {"event": "RUNNER_STOP", **final}); return 0
        if now < a.not_before:
            waiting = {"status": "WAITING_FOR_NOT_BEFORE", "now": iso_z(now), "not_before": iso_z(a.not_before)}
            write_status(status_path, waiting)
            if a.once:
                print(json.dumps(waiting, indent=2)); return 0
            time.sleep(min(a.poll_seconds, max(1, int((a.not_before - now).total_seconds())))); continue
        try:
            result = run_iteration(a)
            write_status(status_path, result)
            append_event(events, {"event": "ITERATION", **result})
        except Exception as exc:
            failure = {"status": "FAIL_CLOSED", "error": str(exc)}
            write_status(status_path, failure); append_event(events, {"event": "FAIL_CLOSED", **failure})
            print(json.dumps(failure, indent=2), file=sys.stderr)
            return 2
        if a.once:
            print(json.dumps(result, indent=2)); return 0
        time.sleep(a.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
