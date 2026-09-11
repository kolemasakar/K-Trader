from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from ktrader.history import load_mtf_bundle, load_universe_archive
from ktrader.replay import (
    load_prospective_control_shard,
    merge_prospective_control_shards,
    run_prospective_control_shard,
    write_prospective_control_report,
    write_prospective_control_shard,
)
from ktrader.runtime.models import RuntimeScannerConfig


def _utc(value: str) -> datetime:
    text = value.strip()
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware UTC")
    return parsed.astimezone(timezone.utc)


def _discover_bundles(root: Path) -> dict[str, object]:
    if not root.is_dir():
        raise SystemExit(f"bundle root does not exist or is not a directory: {root}")
    bundles = {}
    for manifest in sorted(root.rglob("bundle.json")):
        bundle = load_mtf_bundle(manifest.parent)
        symbol = bundle.manifest.canonical_symbol
        if symbol in bundles:
            raise SystemExit(f"multiple MTF bundles discovered for symbol {symbol}")
        bundles[symbol] = bundle
    if not bundles:
        raise SystemExit(f"no MTF bundle.json files found under {root}")
    return bundles


def _run(args: argparse.Namespace) -> None:
    archive = load_universe_archive(args.archive)
    bundles = _discover_bundles(args.bundle_root)
    scanner = RuntimeScannerConfig(
        setup_interval=args.setup_interval,
        setup_max_age_bars=args.setup_max_age_bars,
    )

    resume = None
    if args.resume:
        if args.output.exists():
            resume = load_prospective_control_shard(args.output)
    elif args.output.exists():
        raise SystemExit(f"output already exists; use --resume or choose another path: {args.output}")

    checkpoint_counter = 0

    def checkpoint(shard):
        nonlocal checkpoint_counter
        checkpoint_counter += 1
        if checkpoint_counter % args.checkpoint_every == 0:
            write_prospective_control_shard(args.output, shard)

    shard = run_prospective_control_shard(
        archive,
        bundles,
        scanner_config=scanner,
        start=args.start,
        end=args.end,
        analysis_limit=args.analysis_limit,
        max_context_age_seconds=args.max_context_age_seconds,
        shard_index=args.shard_index,
        shard_count=args.shard_count,
        resume=resume,
        max_new_cutoffs=args.max_new_cutoffs,
        checkpoint_function=checkpoint,
        checkpoint_every=1,
    )
    write_prospective_control_shard(args.output, shard)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "schema_version": shard.schema_version,
                "provider_id": shard.provider_id,
                "archive_sha256": shard.archive_sha256,
                "scanner_config_sha256": shard.scanner_config_sha256,
                "shard_index": shard.shard_index,
                "shard_count": shard.shard_count,
                "processed_cutoffs": len(shard.cutoffs),
                "expected_cutoffs": shard.expected_cutoff_count,
                "complete": shard.complete,
                "shard_sha256": shard.shard_sha256,
            },
            sort_keys=True,
        )
    )


def _merge(args: argparse.Namespace) -> None:
    shards = [load_prospective_control_shard(path) for path in args.shard]
    report = merge_prospective_control_shards(shards)
    write_prospective_control_report(args.output, report)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "schema_version": report.schema_version,
                "provider_id": report.provider_id,
                "logical_cutoffs": report.logical_cutoffs,
                "selected_context_cutoffs": report.selected_context_cutoffs,
                "symbol_slots": report.symbol_slots,
                "history_pass_slots": report.history_pass_slots,
                "history_fail_slots": report.history_fail_slots,
                "analysis_error_slots": report.analysis_error_slots,
                "decision_records": report.decision_records,
                "unique_tradable_signal_count": report.unique_tradable_signal_count,
                "report_sha256": report.report_sha256,
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run deterministic, resumable Phase 11G prospective-control analysis"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="run or resume one deterministic shard")
    run.add_argument("--archive", required=True, type=Path)
    run.add_argument("--bundle-root", required=True, type=Path)
    run.add_argument("--start", required=True, type=_utc)
    run.add_argument("--end", required=True, type=_utc)
    run.add_argument("--output", required=True, type=Path)
    run.add_argument("--analysis-limit", type=int, default=20)
    run.add_argument("--max-context-age-seconds", type=float, default=300.0)
    run.add_argument("--setup-interval", choices=("5m", "15m", "1h"), default="5m")
    run.add_argument("--setup-max-age-bars", type=int, default=12)
    run.add_argument("--shard-index", type=int, default=0)
    run.add_argument("--shard-count", type=int, default=1)
    run.add_argument("--resume", action="store_true")
    run.add_argument("--checkpoint-every", type=int, default=5)
    run.add_argument(
        "--max-new-cutoffs",
        type=int,
        default=None,
        help="Optional bounded unit of work; rerun with --resume to continue.",
    )
    run.set_defaults(func=_run)

    merge = subparsers.add_parser("merge", help="merge a complete deterministic shard set")
    merge.add_argument("--shard", required=True, type=Path, action="append")
    merge.add_argument("--output", required=True, type=Path)
    merge.set_defaults(func=_merge)

    args = parser.parse_args()
    if args.command == "run" and args.checkpoint_every <= 0:
        parser.error("--checkpoint-every must be positive")
    args.func(args)


if __name__ == "__main__":
    main()
