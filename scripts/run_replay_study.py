from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from ktrader.history import load_mtf_bundle
from ktrader.outcomes import OutcomeRepository
from ktrader.replay import (
    ReplayStudyConfig,
    build_study_run_provenance,
    load_replay_context,
    load_study_cohort,
    run_replay_study,
    write_replay_study,
    write_study_run_provenance,
)
from ktrader.runtime.models import RuntimeScannerConfig


def _utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = value.strip()
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware UTC")
    return parsed.astimezone(timezone.utc)


def _build_study_config(args: argparse.Namespace) -> ReplayStudyConfig:
    return ReplayStudyConfig(
        step_bars=args.step_bars,
        horizon_bars=args.horizon_bars,
        start=args.start,
        end=args.end,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run full-engine chronological K-Trader replay over an MTF bundle"
    )
    parser.add_argument("--bundle", required=True, type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--context", type=Path, help="Legacy standalone replay context")
    source.add_argument(
        "--cohort",
        type=Path,
        help="Canonical Phase 11G path: load the bundle symbol context from a verified study cohort",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--outcome-db", required=True, type=Path)
    parser.add_argument(
        "--provenance-output",
        type=Path,
        default=None,
        help="Optional provenance path. Requires --cohort; defaults to <output>.provenance.json.",
    )
    parser.add_argument("--step-bars", type=int, default=1)
    parser.add_argument(
        "--horizon-bars",
        type=int,
        default=None,
        help="Explicit 5m outcome horizon. Omit to leave the horizon unbounded by this study.",
    )
    parser.add_argument(
        "--start",
        type=_utc,
        default=None,
        help="Optional inclusive UTC replay cutoff lower bound.",
    )
    parser.add_argument(
        "--end",
        type=_utc,
        default=None,
        help="Optional inclusive UTC replay cutoff upper bound.",
    )
    parser.add_argument(
        "--setup-interval",
        choices=("5m", "15m", "1h"),
        default="5m",
        help="Setup/evidence timeframe used by the canonical analyzer.",
    )
    parser.add_argument(
        "--setup-max-age-bars",
        type=int,
        default=12,
        help="Maximum setup age in bars of --setup-interval; expiry is strictly greater than this boundary.",
    )
    args = parser.parse_args()

    if args.provenance_output is not None and args.cohort is None:
        raise SystemExit("--provenance-output requires --cohort")

    bundle = load_mtf_bundle(args.bundle)
    cohort_sha256: str | None = None
    if args.cohort is not None:
        cohort = load_study_cohort(args.cohort)
        if cohort.provider_id != bundle.manifest.provider_id:
            raise SystemExit("cohort provider does not match MTF bundle")
        symbol = bundle.manifest.canonical_symbol
        if symbol not in cohort.contexts:
            raise SystemExit(f"bundle symbol {symbol} is absent from cohort")
        context = cohort.contexts[symbol]
        cohort_sha256 = cohort.cohort_sha256
    else:
        assert args.context is not None
        context = load_replay_context(args.context)

    scanner_config = RuntimeScannerConfig(
        setup_interval=args.setup_interval,
        setup_max_age_bars=args.setup_max_age_bars,
    )
    study_config = _build_study_config(args)
    repository = OutcomeRepository(args.outcome_db)
    try:
        result = run_replay_study(
            bundle,
            context,
            scanner_config=scanner_config,
            study_config=study_config,
            outcome_repository=repository,
        )
        output = write_replay_study(args.output, result)
        provenance_output: Path | None = None
        provenance_sha256: str | None = None
        if cohort_sha256 is not None:
            provenance = build_study_run_provenance(
                result,
                output,
                context,
                scanner_config,
                study_config,
                cohort_sha256=cohort_sha256,
            )
            provenance_output = args.provenance_output or Path(str(output) + ".provenance.json")
            write_study_run_provenance(provenance_output, provenance)
            provenance_sha256 = provenance.provenance_sha256

        print(
            json.dumps(
                {
                    "output": str(output),
                    "provenance_output": str(provenance_output) if provenance_output is not None else None,
                    "provenance_sha256": provenance_sha256,
                    "study_id": result.study_id,
                    "bundle_sha256": result.bundle_sha256,
                    "provider_id": result.provider_id,
                    "symbol": result.canonical_symbol,
                    "setup_interval": scanner_config.setup_interval,
                    "setup_max_age_bars": scanner_config.setup_max_age_bars,
                    "setup_max_age_seconds": scanner_config.setup_max_age_seconds,
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
