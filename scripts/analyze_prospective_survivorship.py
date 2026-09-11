#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ktrader.replay.output_lock import OutputLockError, exclusive_output_lock
from ktrader.replay.prospective import load_prospective_control_shard
from ktrader.replay.survivorship import (
    analyze_prospective_survivorship,
    write_prospective_survivorship_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze Phase 11G prospective-control shards for record-level and "
            "distinct-primary-level survivorship."
        )
    )
    parser.add_argument(
        "--shard",
        action="append",
        type=Path,
        required=True,
        help="Complete prospective-control shard. Repeat for multiple shards/windows.",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        with exclusive_output_lock(args.output):
            shards = tuple(load_prospective_control_shard(path) for path in args.shard)
            report = analyze_prospective_survivorship(shards)
            write_prospective_survivorship_report(args.output, report)
    except OutputLockError as exc:
        parser.error(str(exc))

    print(
        json.dumps(
            {
                "output": str(args.output),
                "schema_version": report["schema_version"],
                "logical_cutoffs": report["logical_cutoffs"],
                "record_funnel": report["record_funnel"],
                "unique_primary_level_funnel": report["unique_primary_level_funnel"],
                "analysis_sha256": report["analysis_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
