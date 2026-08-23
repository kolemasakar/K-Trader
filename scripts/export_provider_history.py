from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path

from ktrader.history import (
    collect_deep_provider_history,
    collect_provider_history,
    write_history_dataset,
)
from ktrader.providers.registry import create_provider


def _utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = value.strip()
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError("--as-of must be timezone-aware UTC")
    return parsed.astimezone(timezone.utc)


async def _run(args: argparse.Namespace) -> None:
    provider = create_provider(args.provider)
    try:
        instruments = await provider.list_instruments()
        symbol = args.symbol.upper()
        instrument = next((item for item in instruments if item.symbol == symbol), None)
        if instrument is None:
            raise SystemExit(f"symbol {symbol} not found on {args.provider}")
        page_capacity = provider.capabilities.max_kline_page_size or 0
        deep = args.deep or args.bars > page_capacity
        if deep:
            dataset = await collect_deep_provider_history(
                provider,
                instrument,
                args.interval,
                max_bars=args.bars,
                fetched_at=args.as_of,
                max_pages=args.max_pages,
            )
        else:
            dataset = await collect_provider_history(
                provider,
                instrument,
                args.interval,
                max_bars=args.bars,
                fetched_at=args.as_of,
            )
        output = write_history_dataset(args.output, dataset)
        manifest = dataset.manifest
        print(json.dumps({
            "output": str(output),
            "provider_id": manifest.provider_id,
            "symbol": manifest.canonical_symbol,
            "interval": manifest.interval,
            "candle_count": manifest.candle_count,
            "actual_start": manifest.actual_start.isoformat().replace("+00:00", "Z"),
            "actual_end": manifest.actual_end.isoformat().replace("+00:00", "Z"),
            "content_sha256": manifest.content_sha256,
            "deep_pagination": deep,
        }, sort_keys=True))
    finally:
        await provider.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export provider-recorded closed candles to K-Trader history JSONL")
    parser.add_argument("--provider", required=True, choices=("binance_usdm", "bybit_linear"))
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--interval", required=True, choices=("5m", "15m", "1h", "4h", "1d"))
    parser.add_argument("--bars", type=int, default=1000)
    parser.add_argument("--deep", action="store_true", help="force backward multi-page collection")
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--as-of", type=_utc)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
