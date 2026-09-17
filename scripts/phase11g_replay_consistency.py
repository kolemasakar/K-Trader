#!/usr/bin/env python3
"""Verify immutable prior Phase 11G family outcomes across accepted cutoffs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TOL = 3e-9


def load(path: Path) -> dict[str, dict]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return {r["setup_family_id"]: r for r in rows}


def close(a, b) -> bool:
    if a is None or b is None:
        return a is b
    return abs(float(a) - float(b)) <= TOL


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prior", type=Path, required=True)
    ap.add_argument("--current", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    prior = load(args.prior)
    current = load(args.current)
    errors = []
    checked = 0
    for fid, old in prior.items():
        if fid not in current:
            errors.append({"setup_family_id": fid, "error": "MISSING_PRIOR_FAMILY"})
            continue
        new = current[fid]
        if old.get("resolved"):
            checked += 1
            fields = ("primary_symbol", "primary_side", "primary_entry_time", "terminal_state")
            for field in fields:
                if old.get(field) != new.get(field):
                    errors.append({"setup_family_id": fid, "error": "IMMUTABLE_FIELD_CHANGED", "field": field, "prior": old.get(field), "current": new.get(field)})
            for field in ("realized_R", "mfe_R", "mae_R"):
                if not close(old.get(field), new.get(field)):
                    errors.append({"setup_family_id": fid, "error": "IMMUTABLE_NUMERIC_CHANGED", "field": field, "prior": old.get(field), "current": new.get(field)})

    report = {
        "schema_version": "ktrader.phase11g_replay_consistency.v1",
        "status": "PASS" if not errors else "FAIL_CLOSED",
        "prior_family_count": len(prior),
        "current_family_count": len(current),
        "resolved_prior_families_checked": checked,
        "error_count": len(errors),
        "errors": errors,
        "holdout_opened": False,
        "production_action": False,
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
