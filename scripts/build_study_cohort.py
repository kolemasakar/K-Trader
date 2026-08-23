from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from ktrader.history import load_universe_archive
from ktrader.replay import build_study_cohort, write_study_cohort


def _utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = value.strip()
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware UTC")
    return parsed.astimezone(timezone.utc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reproducible K-Trader replay contexts from captured universe snapshots")
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--start", type=_utc)
    parser.add_argument("--end", type=_utc)
    parser.add_argument("--symbols", nargs="*")
    parser.add_argument("--max-context-age-seconds", type=float, default=300.0)
    args = parser.parse_args()

    archive = load_universe_archive(args.archive)
    cohort = build_study_cohort(
        archive,
        start=args.start,
        end=args.end,
        symbols=args.symbols or None,
        max_context_age_seconds=args.max_context_age_seconds,
    )
    root = write_study_cohort(args.output, cohort)
    print(json.dumps({
        "output": str(root),
        "schema_version": cohort.schema_version,
        "provider_id": cohort.provider_id,
        "start": cohort.start.isoformat().replace("+00:00", "Z"),
        "end": cohort.end.isoformat().replace("+00:00", "Z"),
        "symbols": list(cohort.symbols),
        "snapshot_count": len(cohort.snapshot_digests),
        "cohort_sha256": cohort.cohort_sha256,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
