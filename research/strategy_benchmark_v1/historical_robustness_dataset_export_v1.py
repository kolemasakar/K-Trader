#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import re
from datetime import datetime, timezone

from ktrader.history.collector import collect_deep_provider_history
from ktrader.history.dataset import write_history_dataset
from ktrader.providers.base import ProviderError
from ktrader.providers.registry import create_provider

DEPTHS = {"1d": 500, "1h": 9060, "15m": 35640}
ORDER = ("1d", "1h", "15m")
WINDOW_REQUIREMENTS = {
    "R90": {"eval_m15": 8640, "m15": 9240, "1h": 2460},
    "R180": {"eval_m15": 17280, "m15": 17880, "1h": 4620},
    "R365": {"eval_m15": 35040, "m15": 35640, "1h": 9060},
}
INSUFFICIENT = re.compile(r"insufficient deep history: requested (\d+), collected (\d+) within (\d+) pages")


def utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError("UTC timestamp required")
    return parsed.astimezone(timezone.utc)


def z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


async def collect_interval(provider, instrument, interval: str, requested: int, cutoff: datetime, max_pages: int):
    try:
        dataset = await collect_deep_provider_history(
            provider,
            instrument,
            interval,
            max_bars=requested,
            fetched_at=cutoff,
            max_pages=max_pages,
        )
        return dataset, {"requested": requested, "actual": requested, "age_limited": False}
    except ProviderError as exc:
        match = INSUFFICIENT.search(str(exc))
        if not match:
            raise
        actual = int(match.group(2))
        if actual <= 0:
            raise
        dataset = await collect_deep_provider_history(
            provider,
            instrument,
            interval,
            max_bars=actual,
            fetched_at=cutoff,
            max_pages=max_pages,
        )
        return dataset, {"requested": requested, "actual": actual, "age_limited": True}


async def run(args):
    protocol = json.loads(pathlib.Path(args.protocol).read_text())
    panel = list(protocol["primary_panel"]["symbols"])
    output = pathlib.Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    provider = create_provider(args.provider)
    rows = []
    try:
        instruments = {item.symbol: item for item in await provider.list_instruments()}
        for symbol in panel:
            instrument = instruments.get(symbol)
            if instrument is None:
                rows.append({"symbol": symbol, "status": "MISSING_INSTRUMENT"})
                continue
            depths = {}
            files = {}
            for interval in ORDER:
                dataset, meta = await collect_interval(
                    provider, instrument, interval, DEPTHS[interval], args.as_of, args.max_pages
                )
                target = output / "bundles" / symbol / f"{interval}.jsonl"
                write_history_dataset(target, dataset)
                depths[interval] = meta
                files[interval] = {
                    "path": str(target),
                    "content_sha256": dataset.manifest.content_sha256,
                    "actual_start": z(dataset.manifest.actual_start),
                    "actual_end": z(dataset.manifest.actual_end),
                    "candle_count": dataset.manifest.candle_count,
                }
            readiness = {}
            for name, req in WINDOW_REQUIREMENTS.items():
                reasons = []
                if depths["15m"]["actual"] < req["m15"]:
                    reasons.append("M15_AGE_LIMITED")
                if depths["1h"]["actual"] < req["1h"]:
                    reasons.append("H1_AGE_LIMITED")
                readiness[name] = {"ready": not reasons, "reasons": reasons}
            row = {
                "symbol": symbol,
                "status": "PASS",
                "provider_id": provider.provider_id,
                "as_of": z(args.as_of),
                "depths": depths,
                "files": files,
                "window_readiness_pre_outcome": readiness,
            }
            rows.append(row)
            print(json.dumps(row, sort_keys=True), flush=True)
    finally:
        await provider.close()

    summary = {
        "schema_version": "ktrader.frozen_v2_2.historical_robustness_dataset.v1",
        "research_only": True,
        "outcome_free_readiness": True,
        "provider_id": args.provider,
        "as_of": z(args.as_of),
        "depths_requested": DEPTHS,
        "window_requirements": WINDOW_REQUIREMENTS,
        "panel_size": len(panel),
        "rows": rows,
    }
    summary_path = output / "dataset_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("SUMMARY", summary_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="binance_usdm")
    parser.add_argument("--protocol", default="/data/research/phase11g/strategy_benchmark_v1/protocol.json")
    parser.add_argument("--as-of", required=True, type=utc)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-pages", type=int, default=100)
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
