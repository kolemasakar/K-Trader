from __future__ import annotations

import argparse
import json
from pathlib import Path

from ktrader.history import load_mtf_bundle
from ktrader.outcomes import OutcomeRepository
from ktrader.replay import (
    ReplayStudyConfig,
    load_replay_context,
    run_replay_study,
    write_replay_study,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run full-engine chronological K-Trader replay over an MTF bundle"
    )
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--context", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--outcome-db", required=True, type=Path)
    parser.add_argument("--step-bars", type=int, default=1)
    parser.add_argument(
        "--horizon-bars",
        type=int,
        default=None,
        help="Explicit 5m outcome horizon. Omit to leave the horizon unbounded by this study.",
    )
    args = parser.parse_args()

    bundle = load_mtf_bundle(args.bundle)
    context = load_replay_context(args.context)
    repository = OutcomeRepository(args.outcome_db)
    try:
        result = run_replay_study(
            bundle,
            context,
            study_config=ReplayStudyConfig(
                step_bars=args.step_bars,
                horizon_bars=args.horizon_bars,
            ),
            outcome_repository=repository,
        )
        output = write_replay_study(args.output, result)
        print(
            json.dumps(
                {
                    "output": str(output),
                    "study_id": result.study_id,
                    "bundle_sha256": result.bundle_sha256,
                    "provider_id": result.provider_id,
                    "symbol": result.canonical_symbol,
                    "analyzed_cutoffs": result.analyzed_cutoffs,
                    "skipped_insufficient_history": result.skipped_insufficient_history,
                    "skipped_missing_context": result.skipped_missing_context,
                    "unique_tradable_signals": result.unique_tradable_signals,
                    "outcome_counts": dict(result.outcome_counts),
                    "binary_resolved_count": result.binary_resolved_count,
                    "estimated_probability": None,
                },
                sort_keys=True,
            )
        )
    finally:
        repository.close()


if __name__ == "__main__":
    main()
