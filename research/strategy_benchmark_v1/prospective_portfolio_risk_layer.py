#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime
from collections import Counter

DEFAULT_BASE = pathlib.Path("/data/research/phase11g")
DEFAULT_OUTROOT = DEFAULT_BASE / "strategy_benchmark_v1/combined_rules/prospective_portfolio_risk"
RISK_SCENARIOS_PCT = (0.25, 0.50, 1.00, 2.00)


def load_jsonl(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description="Parametric portfolio-risk diagnostic; no production enforcement.")
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--outcomes", required=True)
    ap.add_argument("--diagnostic-report", required=True)
    ap.add_argument("--output-root", default=str(DEFAULT_OUTROOT))
    args = ap.parse_args()

    outcomes = pathlib.Path(args.outcomes)
    families_path = outcomes / "families.jsonl"
    summary_path = outcomes / "summary.json"
    diagnostic_path = pathlib.Path(args.diagnostic_report)
    for path in (families_path, summary_path, diagnostic_path):
        if not path.exists():
            raise SystemExit(f"REQUIRED_FILE_MISSING {path}")

    summary = json.loads(summary_path.read_text())
    diagnostic = json.loads(diagnostic_path.read_text())
    if summary.get("holdout_opened") is not False or summary.get("production_action") is not False:
        raise SystemExit("OUTCOME_GOVERNANCE_INVARIANT_FAILED")
    if diagnostic.get("holdout_opened") is not False or diagnostic.get("production_action") is not False:
        raise SystemExit("DIAGNOSTIC_GOVERNANCE_INVARIANT_FAILED")

    families = load_jsonl(families_path)
    open_rows = [row for row in families if not row.get("resolved")]
    side_counts = Counter(row.get("primary_side") for row in open_rows)
    symbol_counts = Counter(row.get("primary_symbol") for row in open_rows)
    open_n = len(open_rows)
    max_same_side_open = max(side_counts.values(), default=0)

    portfolio = diagnostic.get("portfolio", {})
    max_concurrent_observed = int(portfolio.get("max_concurrent_all") or 0)
    max_concurrent_short = int(portfolio.get("max_concurrent_short") or 0)
    largest_corr = int(portfolio.get("largest_correlated_cohort_size") or 0)

    scenarios = []
    for risk in RISK_SCENARIOS_PCT:
        scenarios.append({
            "risk_per_family_pct": risk,
            "current_open_gross_stop_risk_pct": open_n * risk,
            "current_largest_same_side_open_risk_pct": max_same_side_open * risk,
            "observed_max_concurrent_gross_risk_pct": max_concurrent_observed * risk,
            "observed_max_short_gross_risk_pct": max_concurrent_short * risk,
            "observed_largest_correlated_cohort_risk_pct": largest_corr * risk,
        })

    report = {
        "schema_version": "ktrader.prospective_portfolio_risk.v1",
        "as_of": args.as_of,
        "diagnostic_only": True,
        "production_enforcement": False,
        "holdout_opened": False,
        "production_action": False,
        "current_open_family_count": open_n,
        "current_open_by_side": dict(sorted(side_counts.items())),
        "current_open_by_symbol": dict(sorted(symbol_counts.items())),
        "max_same_side_open_count": max_same_side_open,
        "observed_max_concurrent_all": max_concurrent_observed,
        "observed_max_concurrent_short": max_concurrent_short,
        "observed_largest_correlated_cohort_size": largest_corr,
        "risk_scenarios": scenarios,
        "future_control_contract": {
            "required_parameters": [
                "risk_per_trade_pct",
                "max_portfolio_open_risk_pct",
                "max_same_side_open_risk_pct",
                "max_correlated_cluster_open_risk_pct",
                "max_open_positions",
            ],
            "rule": "pre-trade authorization must fail closed when any configured cap would be exceeded",
            "values_fixed_here": False,
        },
        "interpretation_guard": "This report quantifies concentration risk only. It does not set or authorize production caps.",
        "status": "PASS",
    }

    stamp = datetime.fromisoformat(args.as_of.replace("Z", "+00:00")).strftime("%Y%m%dT%H%M%SZ")
    out = pathlib.Path(args.output_root) / stamp
    out.mkdir(parents=True, exist_ok=False)
    report_path = out / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    print("REPORT", report_path, sha(report_path))


if __name__ == "__main__":
    main()
