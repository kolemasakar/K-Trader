#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime, timezone


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate machine-readable accepted research state manifest.")
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--cycle-summary", required=True)
    ap.add_argument("--ledger-summary", required=True)
    ap.add_argument("--outcomes-summary", required=True)
    ap.add_argument("--evidence-report", required=True)
    ap.add_argument("--risk-report", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    files = [pathlib.Path(value) for value in (
        args.cycle_summary,
        args.ledger_summary,
        args.outcomes_summary,
        args.evidence_report,
        args.risk_report,
    )]
    for path in files:
        if not path.exists():
            raise SystemExit(f"REQUIRED_FILE_MISSING {path}")

    cycle, ledger, outcomes, evidence, risk = map(load_json, files)
    if outcomes.get("as_of") != args.as_of or cycle.get("as_of") != args.as_of:
        raise SystemExit("ASOF_MISMATCH")
    if any(obj.get("holdout_opened") is not False for obj in (cycle, ledger, outcomes, evidence, risk)):
        raise SystemExit("HOLDOUT_INVARIANT_FAILED")
    if any(obj.get("production_action") is not False for obj in (cycle, ledger, outcomes, evidence, risk)):
        raise SystemExit("PRODUCTION_ACTION_INVARIANT_FAILED")

    state = {
        "schema_version": "ktrader.current_research_state.v1",
        "as_of": args.as_of,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "strategy_id": outcomes.get("strategy_id"),
        "resolver_version": outcomes.get("resolver_version"),
        "cycle_status": cycle.get("cycle_status"),
        "panel_size": cycle.get("panel_size"),
        "eligible_observations": outcomes.get("eligible_observation_count"),
        "unique_families": outcomes.get("unique_family_count"),
        "resolved_primary_families": outcomes.get("resolved_primary_family_count"),
        "unresolved_primary_families": outcomes.get("unresolved_primary_family_count"),
        "expectancy_R": outcomes.get("resolved_expectancy_R"),
        "evidence_status": outcomes.get("evidence_status"),
        "confirmation_family_count": evidence.get("confirmation_family_count"),
        "confirmation_resolved_count": evidence.get("confirmation_resolved_count"),
        "current_open_family_count": risk.get("current_open_family_count"),
        "observed_max_concurrent_all": risk.get("observed_max_concurrent_all"),
        "holdout_opened": False,
        "production_action": False,
        "source_hashes": {str(path): sha(path) for path in files},
        "status": "PASS",
    }
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(json.dumps(state, indent=2, sort_keys=True))
    print("REPORT", output, sha(output))


if __name__ == "__main__":
    main()
