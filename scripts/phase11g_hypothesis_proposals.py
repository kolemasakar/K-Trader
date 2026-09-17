#!/usr/bin/env python3
"""Generate research-only hypothesis/ablation proposals after 50 resolved families.

This tool never edits candidate_rule_set_v2_2. It converts exploratory
statistics into versioned proposal records for later independent testing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MIN_RESOLVED = 50


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, required=True)
    ap.add_argument("--statistics", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    state = json.loads(args.state.read_text())
    stats = json.loads(args.statistics.read_text())
    n = int(state.get("resolved_primary_families", 0))
    if state.get("strategy_id") != "candidate_rule_set_v2_2" or state.get("resolver_version") != "v1.3" or state.get("holdout_opened") is not False or state.get("production_action") is not False:
        print(json.dumps({"status": "FAIL_CLOSED", "reason": "INVARIANT_MISMATCH"}, indent=2))
        return 2
    if n < MIN_RESOLVED:
        print(json.dumps({
            "schema_version": "ktrader.phase11g_hypothesis_proposals.v1",
            "status": "BELOW_EVIDENCE_TIER",
            "resolved_primary_families": n,
            "required": MIN_RESOLVED,
            "proposal_count": 0,
            "frozen_strategy_mutated": False,
        }, indent=2))
        return 0

    proposals = []
    for t in stats.get("tests", []):
        proposals.append({
            "hypothesis_id": t.get("name", "unnamed").lower().replace(" ", "_").replace("<", "lt").replace(">", "gt"),
            "source_contrast": t.get("name"),
            "observed_mean_difference_R": t.get("mean_diff_a_minus_b"),
            "permutation_p": t.get("permutation_p_two_sided"),
            "permutation_bh_q": t.get("permutation_bh_q"),
            "fisher_winrate_p": t.get("fisher_winrate_p_two_sided"),
            "status": "PROPOSAL_ONLY",
            "allowed_action": "design independent ablation/OOS test",
            "forbidden_action": "mutate frozen candidate_rule_set_v2_2 in place",
        })

    report = {
        "schema_version": "ktrader.phase11g_hypothesis_proposals.v1",
        "as_of": state.get("as_of"),
        "status": "PASS",
        "evidence_tier": "HYPOTHESES_ABLATION_50_99" if n < 100 else "RECALIBRATION_PROPOSAL_MAY_BE_CONSIDERED",
        "resolved_primary_families": n,
        "proposal_count": len(proposals),
        "proposals": proposals,
        "exploratory_only": True,
        "multiple_comparison_results_preserved": True,
        "frozen_strategy_mutated": False,
        "holdout_opened": False,
        "production_action": False,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
