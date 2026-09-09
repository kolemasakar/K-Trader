from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
from statistics import median

from ktrader.engine.geometry import build_setup_geometry
from ktrader.history import load_mtf_bundle
from ktrader.replay import ReplayStudyConfig, load_study_cohort, run_replay_study
from ktrader.runtime import analyzer as runtime_analyzer
from ktrader.runtime.models import RuntimeScannerConfig


def _utc(value: str) -> datetime:
    text = value.strip()
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware UTC")
    return parsed.astimezone(timezone.utc)


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[index]


def main() -> None:
    parser = argparse.ArgumentParser(description="Study setup lifecycle sensitivity without changing trading hard gates")
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--cohort", required=True, type=Path)
    parser.add_argument("--setup-interval", required=True, choices=("5m", "15m", "1h"))
    parser.add_argument("--ttl-minutes", required=True, type=int, nargs="+")
    parser.add_argument("--start", required=True, type=_utc)
    parser.add_argument("--end", required=True, type=_utc)
    args = parser.parse_args()

    if any(value <= 0 for value in args.ttl_minutes):
        parser.error("all --ttl-minutes values must be positive")

    bundle = load_mtf_bundle(args.bundle)
    cohort = load_study_cohort(args.cohort)
    symbol = bundle.manifest.canonical_symbol
    if symbol not in cohort.contexts:
        raise SystemExit(f"bundle symbol {symbol} is absent from cohort")
    context = cohort.contexts[symbol]

    records: list[dict[str, object]] = []
    original_evaluate = runtime_analyzer.evaluate_candidate

    def instrumented_evaluate(candidate, **kwargs):
        kwargs = dict(kwargs)
        kwargs["setup_max_age_seconds"] = 10**12
        decision = original_evaluate(candidate, **kwargs)
        age_seconds: float | None = None
        try:
            geometry = build_setup_geometry(
                candidate,
                kwargs["setup_candles"],
                levels=kwargs["structure"].levels,
                atr14=kwargs["atr14"],
                atr5d=kwargs["atr5d"],
                day_range=kwargs["day_range"],
                price_tick=kwargs["instrument"].price_tick,
                luft_atr_fraction=kwargs.get("luft_atr_fraction", Decimal("0.02")),
            )
            age_seconds = (kwargs["generated_at"] - geometry.confirmation_time).total_seconds()
        except ValueError:
            pass
        records.append(
            {
                "age_seconds": age_seconds,
                "reason_codes": tuple(decision.reason_codes),
                "side": decision.side,
                "grade": decision.grade,
                "rr": str(decision.rr) if decision.rr is not None else None,
            }
        )
        return decision

    runtime_analyzer.evaluate_candidate = instrumented_evaluate
    try:
        scanner_config = RuntimeScannerConfig(
            setup_interval=args.setup_interval,
            setup_max_age_bars=100000,
        )
        result = run_replay_study(
            bundle,
            context,
            scanner_config=scanner_config,
            study_config=ReplayStudyConfig(start=args.start, end=args.end),
            analysis_function=runtime_analyzer.analyze_candle_snapshot,
        )
    finally:
        runtime_analyzer.evaluate_candidate = original_evaluate

    ages = [float(record["age_seconds"]) for record in records if record["age_seconds"] is not None]
    reason_counts = Counter(reason for record in records for reason in record["reason_codes"])

    sensitivity = []
    for ttl_minutes in sorted(set(args.ttl_minutes)):
        ttl_seconds = ttl_minutes * 60
        expired = sum(1 for record in records if record["age_seconds"] is not None and float(record["age_seconds"]) > ttl_seconds)
        geometry_survivors = sum(1 for record in records if record["age_seconds"] is not None and float(record["age_seconds"]) <= ttl_seconds)
        rr_only_survivors = sum(
            1
            for record in records
            if record["age_seconds"] is not None
            and float(record["age_seconds"]) <= ttl_seconds
            and tuple(record["reason_codes"]) == ("RR_BELOW_3",)
        )
        tradable_survivors = sum(
            1
            for record in records
            if record["age_seconds"] is not None
            and float(record["age_seconds"]) <= ttl_seconds
            and record["side"] != "NO_TRADE"
        )
        sensitivity.append(
            {
                "ttl_minutes": ttl_minutes,
                "expired": expired,
                "geometry_survivors": geometry_survivors,
                "rr_only_survivors": rr_only_survivors,
                "tradable_survivors": tradable_survivors,
            }
        )

    output = {
        "provider_id": bundle.manifest.provider_id,
        "symbol": symbol,
        "bundle_sha256": bundle.manifest.bundle_sha256,
        "cohort_sha256": cohort.cohort_sha256,
        "setup_interval": args.setup_interval,
        "start": args.start.isoformat().replace("+00:00", "Z"),
        "end": args.end.isoformat().replace("+00:00", "Z"),
        "analyzed_cutoffs": result.analyzed_cutoffs,
        "candidate_records": len(records),
        "geometry_records": len(ages),
        "age_minutes": {
            "min": min(ages) / 60 if ages else None,
            "median": median(ages) / 60 if ages else None,
            "p90": _percentile(ages, 0.90) / 60 if ages else None,
            "max": max(ages) / 60 if ages else None,
        },
        "base_reason_counts": dict(sorted(reason_counts.items())),
        "sensitivity": sensitivity,
        "base_unique_tradable_signals": result.unique_tradable_signals,
        "estimated_probability": None,
    }
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
