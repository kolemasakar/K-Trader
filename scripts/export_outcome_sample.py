from __future__ import annotations

import argparse
import json
from pathlib import Path

from ktrader.outcomes import (
    OutcomeRepository,
    build_outcome_sample_from_repository,
    write_outcome_sample,
)
from ktrader.replay import load_study_run_provenance


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export an immutable binary WIN/LOSS outcome sample linked to one replay study"
    )
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--provenance", required=True, type=Path)
    parser.add_argument("--outcome-db", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    provenance = load_study_run_provenance(args.provenance)
    repository = OutcomeRepository(args.outcome_db)
    try:
        sample = build_outcome_sample_from_repository(args.study, provenance, repository)
        output = write_outcome_sample(args.output, sample)
    finally:
        repository.close()

    print(
        json.dumps(
            {
                "output": str(output),
                "schema_version": sample.schema_version,
                "source_study_id": sample.source_study_id,
                "source_replay_study_sha256": sample.source_replay_study_sha256,
                "provider_id": sample.provider_id,
                "symbol": sample.canonical_symbol,
                "record_count": sample.record_count,
                "statuses": list(sample.statuses),
                "content_sha256": sample.content_sha256,
                "estimated_probability": None,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
