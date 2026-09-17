#!/usr/bin/env python3
"""Preflight verifier for the approved Phase 11G data-only pause window."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_STRATEGY = "candidate_rule_set_v2_2"
EXPECTED_RESOLVER = "v1.3"
EXPECTED_PREREG = "2026-09-16T13:00:00Z"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, required=True)
    ap.add_argument("--outcomes", type=Path, required=True)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--risk", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    state = json.loads(args.state.read_text())
    outcomes = json.loads(args.outcomes.read_text())
    evidence = json.loads(args.evidence.read_text())
    risk = json.loads(args.risk.read_text())

    same_as_of = len({state.get("as_of"), outcomes.get("as_of"), evidence.get("as_of"), risk.get("as_of")}) == 1
    checks = {
        "state_pass": state.get("status") == "PASS",
        "strategy_frozen": state.get("strategy_id") == EXPECTED_STRATEGY == outcomes.get("strategy_id"),
        "resolver_pinned": state.get("resolver_version") == EXPECTED_RESOLVER == outcomes.get("resolver_version"),
        "same_as_of": same_as_of,
        "holdout_closed": all(x.get("holdout_opened") is False for x in (state, outcomes, evidence, risk)),
        "production_action_false": all(x.get("production_action") is False for x in (state, outcomes, evidence, risk)),
        "network_not_used_for_resolution": outcomes.get("network_used") is False and evidence.get("network_used") is False,
        "prereg_boundary_pinned": evidence.get("prereg_boundary") == EXPECTED_PREREG,
        "family_accounting": state.get("unique_families") == state.get("resolved_primary_families", 0) + state.get("unresolved_primary_families", 0),
        "evidence_pass": evidence.get("status") == "PASS",
        "risk_pass": risk.get("status") == "PASS",
        "risk_diagnostic_only": risk.get("diagnostic_only") is True and risk.get("production_enforcement") is False,
    }
    errors = [k for k, v in checks.items() if not v]
    report = {
        "schema_version": "ktrader.phase11g_pause_preflight.v1",
        "as_of": state.get("as_of"),
        "status": "PASS" if not errors else "FAIL_CLOSED",
        "checks": checks,
        "errors": errors,
        "resolved_primary_families": state.get("resolved_primary_families"),
        "unresolved_primary_families": state.get("unresolved_primary_families"),
        "confirmation_family_count": state.get("confirmation_family_count"),
        "state_sha256": sha256(args.state),
        "outcomes_sha256": sha256(args.outcomes),
        "evidence_sha256": sha256(args.evidence),
        "risk_sha256": sha256(args.risk),
        "development_paused": True,
        "data_collection_authorized": True,
        "holdout_open_authorized": False,
        "phase12_active": False,
        "production_trading_authorized": False,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
