#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
from collections import defaultdict
from datetime import datetime, timezone


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description="Read-only research storage growth diagnostic.")
    ap.add_argument("--root", default="/data/research")
    ap.add_argument("--filesystem-capacity-bytes", type=int, required=True)
    ap.add_argument("--filesystem-used-bytes", type=int, required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    daily = defaultdict(lambda: {"bytes": 0, "files": 0})
    total = 0
    for dirpath, _dirs, files in os.walk(root):
        for filename in files:
            path = pathlib.Path(dirpath) / filename
            try:
                stat = path.stat()
            except OSError:
                continue
            day = datetime.fromtimestamp(stat.st_mtime, timezone.utc).strftime("%Y-%m-%d")
            daily[day]["bytes"] += stat.st_size
            daily[day]["files"] += 1
            total += stat.st_size

    capacity = args.filesystem_capacity_bytes
    used = args.filesystem_used_bytes
    targets = {}
    for percent in (70, 80):
        target = capacity * percent / 100.0
        remaining = max(0.0, target - used)
        cases = {}
        for mib_per_day in (10, 50, 100, 250, 500):
            bytes_per_day = mib_per_day * 1024 * 1024
            cases[f"{mib_per_day}_MiB_per_day"] = remaining / bytes_per_day
        targets[str(percent)] = {
            "target_used_bytes": int(target),
            "additional_bytes_to_threshold": int(remaining),
            "scenario_days": cases,
        }

    report = {
        "schema_version": "ktrader.research_storage_growth.v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "root": str(root),
        "research_bytes": total,
        "filesystem_capacity_bytes": capacity,
        "filesystem_used_bytes": used,
        "filesystem_used_pct": used / capacity * 100 if capacity else None,
        "daily_file_mtime_bytes": dict(sorted(daily.items())),
        "threshold_forecast_scenarios": targets,
        "interpretation_guard": "Daily mtime volume includes one-off research bursts; scenario forecasts are planning ranges, not a deterministic forecast.",
        "retention_timer_change_authorized": False,
        "status": "PASS",
    }
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    print("REPORT", output, sha(output))


if __name__ == "__main__":
    main()
