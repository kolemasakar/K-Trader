#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime, timezone
from collections import Counter, defaultdict

DEFAULT_BASE = pathlib.Path("/data/research/phase11g")
DEFAULT_LEDGER = DEFAULT_BASE / "strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger/deduplicated_events.jsonl"
DEFAULT_OUTROOT = DEFAULT_BASE / "strategy_benchmark_v1/combined_rules/prospective_evidence_tracker"
PREREG_BOUNDARY = "2026-09-16T13:00:00Z"
H1_LOW_THRESHOLD = 0.9033277894201235


def utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_jsonl(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primary_events(events: list[dict]) -> dict[str, dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in events:
        if row.get("status") == "ELIGIBLE_SHADOW_SETUP":
            groups[row["setup_family_id"]].append(row)
    out = {}
    for family, rows in groups.items():
        rows.sort(key=lambda r: (
            r.get("entry_time") or "",
            r.get("signal_bar_open_time") or "",
            r.get("symbol") or "",
            r.get("side") or "",
        ))
        out[family] = rows[0]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Fail-closed discovery/confirmation evidence tracker.")
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--outcomes", required=True)
    ap.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    ap.add_argument("--output-root", default=str(DEFAULT_OUTROOT))
    ap.add_argument("--prereg-boundary", default=PREREG_BOUNDARY)
    ap.add_argument("--h1-low-threshold", type=float, default=H1_LOW_THRESHOLD)
    args = ap.parse_args()

    as_of = utc(args.as_of)
    boundary = utc(args.prereg_boundary)
    if as_of <= boundary:
        raise SystemExit("ASOF_NOT_AFTER_PREREG_BOUNDARY")

    ledger_path = pathlib.Path(args.ledger)
    outcomes = pathlib.Path(args.outcomes)
    families_path = outcomes / "families.jsonl"
    summary_path = outcomes / "summary.json"
    for path in (ledger_path, families_path, summary_path):
        if not path.exists():
            raise SystemExit(f"REQUIRED_FILE_MISSING {path}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    invariants = {
        "holdout_opened_false": summary.get("holdout_opened") is False,
        "production_action_false": summary.get("production_action") is False,
        "network_used_false": summary.get("network_used") is False,
        "outcomes_as_of_matches": summary.get("as_of") == args.as_of,
    }
    if not all(invariants.values()):
        raise SystemExit("OUTCOME_GOVERNANCE_INVARIANT_FAILED " + json.dumps(invariants, sort_keys=True))

    events = load_jsonl(ledger_path)
    prim = primary_events(events)
    fam_rows = load_jsonl(families_path)
    fam_map = {row["setup_family_id"]: row for row in fam_rows}
    if set(prim) != set(fam_map):
        raise SystemExit("PRIMARY_FAMILY_SET_MISMATCH " + json.dumps({
            "missing_outcome": sorted(set(prim) - set(fam_map)),
            "missing_ledger": sorted(set(fam_map) - set(prim)),
        }, sort_keys=True))

    rows = []
    future_or_equal = []
    for family in sorted(prim):
        event = prim[family]
        fam = fam_map[family]
        entry = utc(event["entry_time"])
        if entry >= as_of:
            future_or_equal.append({"family": family, "entry_time": event["entry_time"]})
        h1_sep = (event.get("frozen_features") or {}).get("h1_ema_sep_atr")
        next_level = event.get("level_v2_h1_next_level_R")
        cohort = "CONFIRMATION" if entry >= boundary else "DISCOVERY"
        h1_group = None
        if event.get("side") == "SHORT" and h1_sep is not None:
            h1_group = "LOW" if float(h1_sep) < args.h1_low_threshold else "REST"
        rows.append({
            "setup_family_id": family,
            "symbol": event["symbol"],
            "side": event["side"],
            "entry_time": event["entry_time"],
            "cohort": cohort,
            "h1_ema_sep_atr": h1_sep,
            "h1_group": h1_group,
            "obstacle_inside_1R": next_level is not None and float(next_level) < 1.0,
            "obstacle_inside_3R": next_level is not None and float(next_level) < 3.0,
            "resolved": bool(fam.get("resolved")),
            "terminal_state": fam.get("terminal_state"),
            "realized_R": fam.get("realized_R"),
        })
    if future_or_equal:
        raise SystemExit("FUTURE_ENTRY_CONTAMINATION " + json.dumps(future_or_equal, sort_keys=True))

    confirmation = [row for row in rows if row["cohort"] == "CONFIRMATION"]
    discovery = [row for row in rows if row["cohort"] == "DISCOVERY"]
    conf_resolved = [row for row in confirmation if row["resolved"]]
    conf_short = [row for row in confirmation if row["side"] == "SHORT"]
    conf_short_resolved = [row for row in conf_short if row["resolved"]]
    h1_counts = Counter(
        (row["h1_group"], "resolved" if row["resolved"] else "unresolved")
        for row in conf_short if row["h1_group"]
    )

    report = {
        "schema_version": "ktrader.prospective_evidence_tracker.v1",
        "as_of": args.as_of,
        "prereg_boundary": args.prereg_boundary,
        "h1_low_threshold": args.h1_low_threshold,
        "diagnostic_only": True,
        "holdout_opened": False,
        "production_action": False,
        "network_used": False,
        "invariants": invariants,
        "ledger_sha256": sha(ledger_path),
        "outcomes_summary_sha256": sha(summary_path),
        "family_count": len(rows),
        "discovery_family_count": len(discovery),
        "confirmation_family_count": len(confirmation),
        "confirmation_resolved_count": len(conf_resolved),
        "confirmation_unresolved_count": len(confirmation) - len(conf_resolved),
        "confirmation_short_count": len(conf_short),
        "confirmation_short_resolved_count": len(conf_short_resolved),
        "confirmation_h1_counts": {
            f"{group}_{status}": count for (group, status), count in sorted(h1_counts.items())
        },
        "confirmation_obstacle_counts": {
            "inside_1R_total": sum(row["obstacle_inside_1R"] for row in confirmation),
            "inside_1R_resolved": sum(row["obstacle_inside_1R"] and row["resolved"] for row in confirmation),
            "inside_3R_total": sum(row["obstacle_inside_3R"] for row in confirmation),
            "inside_3R_resolved": sum(row["obstacle_inside_3R"] and row["resolved"] for row in confirmation),
        },
        "confirmation_families": confirmation,
        "status": "PASS",
    }

    stamp = as_of.strftime("%Y%m%dT%H%M%SZ")
    out = pathlib.Path(args.output_root) / stamp
    out.mkdir(parents=True, exist_ok=False)
    (out / "families.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    report_path = out / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    print("REPORT", report_path, sha(report_path))


if __name__ == "__main__":
    main()
