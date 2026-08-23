from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from ktrader.history import collect_provider_history, write_history_dataset
from ktrader.providers.registry import create_provider


async def _run(args: argparse.Namespace) -> None:
    provider = create_provider(args.provider)
    try:
        instruments = await provider.list_instruments()
        symbol = args.symbol.upper()
        instrument = next((item for item in instruments if item.symbol == symbol), None)
        if instrument is None:
            raise SystemExit(f"symbol {symbol} not found on {args.provider}")
        dataset = await collect_provider_history(
            provider,
            instrument,
            args.interval,
            max_bars=args.bars,
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
        }, sort_keys=True))
    finally:
        await provider.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export provider-recorded closed candles to K-Trader history JSONL")
    parser.add_argument("--provider", required=True, choices=("binance_usdm", "bybit_linear"))
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--interval", required=True, choices=("5m", "15m", "1h", "4h", "1d"))
    parser.add_argument("--bars", type=int, default=1000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
