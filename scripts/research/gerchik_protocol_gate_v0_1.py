"""Read-only completeness gate for declared research protocols, not approval.

This validates declarations and stage linkage; it does not certify that source
artifacts, cost estimates, strategy implementations or holdout claims are true.
"""
import argparse
import hashlib
import json
import re
from math import isfinite
from pathlib import Path

FAMILIES = {
    "S1": "LEVEL_REJECTION", "S2": "BREAKOUT_CONTINUATION",
    "S3": "BREAKOUT_RETEST", "S4": "SINGLE_FALSE_BREAKOUT",
    "S5": "MULTIBAR_FALSE_BREAKOUT", "S6": "TREND_RANGE_BREAKOUT",
}


def fingerprint(manifest):
    """Comparable experiment digest: target/stage evidence excluded only."""
    comparable = {k: v for k, v in manifest.items()
                  if k not in {"target_r", "prior_1r"}}
    payload = json.dumps(comparable, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def audit_protocol(manifest):
    blockers = []

    def require(ok, code):
        if not ok:
            blockers.append(code)

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def digest(value, length=64):
        return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{%d}" % length, value) is not None

    def number(value):
        return type(value) in (int, float) and isfinite(value)

    def obj(value):
        return value if isinstance(value, dict) else {}

    if not isinstance(manifest, dict):
        return {"status": "BLOCKED", "blockers": ["MANIFEST_OBJECT_REQUIRED"],
                "comparison_sha256": None}
    require(manifest.get("schema") == "ktrader.gerchik.protocol.v0.1", "SCHEMA")
    require(digest(manifest.get("code_commit"), 40), "CODE_COMMIT")
    require(manifest.get("target_r") in (1, 3) and type(manifest.get("target_r")) is int,
            "TARGET_1R_OR_3R")
    data = obj(manifest.get("data"))
    require(digest(data.get("inventory_sha256")), "INPUT_INVENTORY_HASH")
    symbols = data.get("symbols")
    require(isinstance(symbols, list) and bool(symbols) and all(text(s) for s in symbols)
            and len(set(symbols)) == len(symbols), "UNIQUE_SYMBOLS")
    start, end = data.get("start_ms"), data.get("end_ms")
    require(type(start) is int and type(end) is int and start < end, "DATA_BOUNDARIES")
    period = obj(manifest.get("study"))
    a, b = period.get("start_ms"), period.get("end_ms")
    require(all(type(x) is int for x in (start, end, a, b))
            and start <= a < b <= end, "STUDY_BOUNDARIES_AND_WARMUP")
    require(text(period.get("warmup_policy")), "WARMUP_POLICY")
    require(period.get("claim") in ("EXPLORATORY", "INDEPENDENT_VALIDATION"), "STUDY_CLAIM")
    if period.get("claim") == "INDEPENDENT_VALIDATION":
        holdout = obj(period.get("holdout"))
        require(holdout.get("previously_inspected") is False
                and digest(holdout.get("reservation_sha256"))
                and text(holdout.get("reservation_provenance")), "UNTOUCHED_CONTROL_EVIDENCE")
    levels = obj(manifest.get("levels"))
    require(levels.get("atr_used") is False, "ATR_FREE_LEVELS")
    require(levels.get("atr_diagnostic") == "ITERATIVE_D1_ATR5_V2", "CANONICAL_ATR5_V2")
    for key in ("ledger_sha256", "specification_sha256"):
        require(digest(levels.get(key)), "LEVEL_" + key.upper())
    for key in ("tolerance_anchor", "tick_rounding", "causal_known_at_policy", "entry_precision"):
        require(text(levels.get(key)), "LEVEL_" + key.upper())
    require(levels.get("week_policy") == "COMPLETE_UTC_MON_SUN_FROM_D1", "CLOSED_W1_POLICY")
    strategies = manifest.get("strategies")
    valid = isinstance(strategies, list) and all(isinstance(s, dict) for s in strategies)
    ids = [s.get("id") for s in strategies] if valid else []
    require(len(ids) == 6 and all(type(s) is str for s in ids)
            and set(ids) == set(FAMILIES), "SIX_UNIQUE_STRATEGIES")
    if valid:
        for strategy in strategies:
            sid = strategy.get("id")
            if not isinstance(sid, str) or sid not in FAMILIES:
                continue
            require(strategy.get("family") == FAMILIES[sid], sid + "_IDENTITY")
            require(digest(strategy.get("executable_spec_sha256")), sid + "_EXECUTABLE_SPEC")
            require(strategy.get("unresolved") == [], sid + "_UNRESOLVED_PARAMETERS")
            require(text(strategy.get("parameter_migration")), sid + "_PARAMETER_MIGRATION")
            if sid == "S3":
                require(strategy.get("stop_basis") == "BEYOND_LEVEL", "S3_STOP_BEYOND_LEVEL")
    execution = obj(manifest.get("execution"))
    require(execution.get("entry") == "NEXT_OPEN", "ENTRY_POLICY")
    require(execution.get("collision_policy") in ("AMBIGUOUS", "STOP_FIRST"), "COLLISION_POLICY")
    for key in ("interval_ms", "horizon_bars"):
        require(type(execution.get(key)) is int and execution[key] > 0, "EXECUTION_" + key.upper())
    for key in ("fee_rate", "adverse_fill_cost", "funding_cost_per_unit"):
        value = execution.get(key)
        require(number(value) and (key == "funding_cost_per_unit" or value >= 0),
                "COST_" + key.upper())
    for key in ("cost_provenance", "funding_estimate_policy", "overlap_policy", "calendar_metadata"):
        require(text(execution.get(key)), "EXECUTION_" + key.upper())
    require(execution.get("cost_basis") in ("MEASURED", "DECLARED_PROXY"), "COST_BASIS")
    resources = obj(manifest.get("resources"))
    require(resources.get("archive_read_only") is True, "ARCHIVE_READ_ONLY")
    require(resources.get("free_only") is True, "FREE_ONLY")
    for key in ("memory_mb", "timeout_seconds"):
        require(type(resources.get(key)) is int and resources[key] > 0, "RESOURCE_" + key.upper())
    require(text(resources.get("output_location")), "RESEARCH_OUTPUT_LOCATION")
    try:
        comparison = fingerprint(manifest)
    except (TypeError, ValueError):
        comparison = None
        blockers.append("FINITE_JSON_REQUIRED")
    if manifest.get("target_r") == 3:
        prior = obj(manifest.get("prior_1r"))
        require(prior.get("target_r") == 1 and prior.get("status") == "COMPLETED"
                and digest(prior.get("report_sha256"))
                and comparison is not None and prior.get("comparison_sha256") == comparison,
                "MATCHING_COMPLETED_1R_REQUIRED")
    return {"status": "BLOCKED" if blockers else "DECLARATIONS_COMPLETE",
            "blockers": blockers, "comparison_sha256": comparison,
            "artifact_verification": "NOT_PERFORMED",
            "cost_basis": execution.get("cost_basis"), "study_claim": period.get("claim")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    report = audit_protocol(json.loads(args.manifest.read_text(encoding="utf-8")))
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return 1 if report["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
