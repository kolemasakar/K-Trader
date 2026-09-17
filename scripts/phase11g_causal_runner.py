#!/usr/bin/env python3
"""Sequential Phase 11G M15 causal runner.

This orchestration wrapper advances only closed 15-minute cutoffs, always uses
exactly the immediately preceding accepted outcomes directory, and stops on the
first failure. It never opens holdout, changes candidate rules, or authorizes
production trading.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

UTC = dt.timezone.utc
STEP = dt.timedelta(minutes=15)
DEFAULT_PIPELINE = Path("/tmp/ktrader-runtime-v2/run_prospective_research_pipeline_v2.py")
DEFAULT_BASE = Path("/data/research/phase11g/strategy_benchmark_v1/combined_rules")
DEFAULT_PREREG = "2026-09-16T13:00:00Z"


def parse_utc(value: str) -> dt.datetime:
    x = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if x.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return x.astimezone(UTC)


def tag(x: dt.datetime) -> str:
    return x.strftime("%Y%m%dT%H%M%SZ")


def iso(x: dt.datetime) -> str:
    return x.strftime("%Y-%m-%dT%H:%M:%SZ")


def is_m15(x: dt.datetime) -> bool:
    return x.second == 0 and x.microsecond == 0 and x.minute % 15 == 0


def latest_closed(now: dt.datetime, close_lag_seconds: int) -> dt.datetime:
    safe = now - dt.timedelta(seconds=close_lag_seconds)
    return safe.replace(minute=(safe.minute // 15) * 15, second=0, microsecond=0)


def load_summary(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="first cutoff, UTC ISO8601")
    ap.add_argument("--prior-outcomes", type=Path, required=True)
    ap.add_argument("--stop-at", help="hard final cutoff, UTC ISO8601")
    ap.add_argument("--pipeline", type=Path, default=DEFAULT_PIPELINE)
    ap.add_argument("--base", type=Path, default=DEFAULT_BASE)
    ap.add_argument("--prereg-boundary", default=DEFAULT_PREREG)
    ap.add_argument("--close-lag-seconds", type=int, default=30)
    ap.add_argument("--max-cycles", type=int, default=256)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    start = parse_utc(args.start)
    stop = parse_utc(args.stop_at) if args.stop_at else latest_closed(dt.datetime.now(UTC), args.close_lag_seconds)
    if not is_m15(start) or not is_m15(stop):
        print("FAIL_CLOSED: start/stop must be exact M15 cutoffs", file=sys.stderr)
        return 2
    if stop < start:
        print(json.dumps({"status": "NO_CLOSED_CUTOFF", "start": iso(start), "stop": iso(stop)}))
        return 0
    if not args.pipeline.exists():
        print(f"FAIL_CLOSED: missing pipeline {args.pipeline}", file=sys.stderr)
        return 2
    if not args.prior_outcomes.exists():
        print(f"FAIL_CLOSED: missing prior outcomes {args.prior_outcomes}", file=sys.stderr)
        return 2

    current = start
    prior = args.prior_outcomes
    completed = []
    while current <= stop:
        if len(completed) >= args.max_cycles:
            print("FAIL_CLOSED: max cycle guard reached", file=sys.stderr)
            return 2
        expected_prior_tag = tag(current - STEP)
        if prior.name != expected_prior_tag:
            print(f"FAIL_CLOSED: non-sequential prior {prior.name}, expected {expected_prior_tag}", file=sys.stderr)
            return 2
        out = args.base / "prospective_v2_2_outcomes_offline_v1_3" / tag(current)
        manifest = args.base / "prospective_pipeline_manifests" / f"pipeline_v2_{tag(current)}_execute.json"
        if out.exists() or manifest.exists():
            print(f"FAIL_CLOSED: immutable output already exists for {tag(current)}", file=sys.stderr)
            return 2
        cmd = [
            sys.executable, str(args.pipeline),
            "--as-of", iso(current),
            "--prior-outcomes", str(prior),
            "--prereg-boundary", args.prereg_boundary,
            "--execute",
        ]
        if args.dry_run:
            completed.append({"as_of": iso(current), "prior": str(prior), "mode": "DRY_RUN"})
            prior = out
            current += STEP
            continue
        proc = subprocess.run(cmd, text=True, capture_output=True)
        if proc.returncode != 0:
            print(proc.stdout, end="")
            print(proc.stderr, file=sys.stderr, end="")
            print(f"FAIL_CLOSED: pipeline failed at {iso(current)}", file=sys.stderr)
            return proc.returncode or 2
        summary = out / "summary.json"
        if not summary.exists():
            print(f"FAIL_CLOSED: missing accepted summary {summary}", file=sys.stderr)
            return 2
        s = load_summary(summary)
        if s.get("as_of") != iso(current) or s.get("holdout_opened") is not False or s.get("production_action") is not False or s.get("resolver_version") != "v1.3" or s.get("strategy_id") != "candidate_rule_set_v2_2":
            print(f"FAIL_CLOSED: invariant mismatch at {iso(current)}", file=sys.stderr)
            return 2
        completed.append({"as_of": iso(current), "status": "PASS", "resolved": s.get("resolved_primary_family_count"), "unique": s.get("unique_family_count")})
        prior = out
        current += STEP

    print(json.dumps({
        "schema_version": "ktrader.phase11g_causal_runner.v1",
        "status": "PASS",
        "dry_run": args.dry_run,
        "completed_cycle_count": len(completed),
        "first_cutoff": completed[0]["as_of"] if completed else None,
        "last_cutoff": completed[-1]["as_of"] if completed else None,
        "next_prior_outcomes": str(prior),
        "cycles": completed,
        "holdout_opened": False,
        "production_action": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
