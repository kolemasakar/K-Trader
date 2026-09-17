#!/usr/bin/env python3
"""Fail-closed Phase 11G state/closure monitor.

Reads a machine state manifest only. It never opens holdout, changes strategy
parameters, selects a risk policy, or authorizes production action.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

FROZEN_STRATEGY = "candidate_rule_set_v2_2"
RESOLVER = "v1.3"

def tier(n: int) -> str:
    if n < 30: return "OBSERVATION_ONLY"
    if n < 50: return "DIAGNOSTIC_30_49"
    if n < 100: return "HYPOTHESES_ABLATION_50_99"
    return "RECALIBRATION_PROPOSAL_MAY_BE_CONSIDERED"

def evaluate(state: dict) -> dict:
    errors=[]
    checks={
        "status_pass": state.get("status") == "PASS",
        "strategy_frozen": state.get("strategy_id") == FROZEN_STRATEGY,
        "resolver_pinned": state.get("resolver_version") == RESOLVER,
        "holdout_closed": state.get("holdout_opened") is False,
        "production_action_false": state.get("production_action") is False,
        "family_accounting": state.get("unique_families") == state.get("resolved_primary_families",0)+state.get("unresolved_primary_families",0),
    }
    for k,v in checks.items():
        if not v: errors.append(k)
    n=int(state.get("resolved_primary_families",0))
    return {
        "schema_version":"ktrader.phase11g_guardrails.v1",
        "as_of":state.get("as_of"),
        "status":"PASS" if not errors else "FAIL_CLOSED",
        "checks":checks,
        "errors":errors,
        "resolved_primary_families":n,
        "closure_path_a_shortfall":max(0,100-n),
        "evidence_tier":tier(n),
        "phase12_active":False,
        "holdout_open_authorized":False,
        "production_trading_authorized":False,
    }

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("state",type=Path); ap.add_argument("--output",type=Path)
    a=ap.parse_args(); report=evaluate(json.loads(a.state.read_text()))
    text=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text)
    print(text,end=""); return 0 if report["status"]=="PASS" else 2
if __name__=="__main__": raise SystemExit(main())
