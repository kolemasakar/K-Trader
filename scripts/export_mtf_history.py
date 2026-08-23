from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path

from ktrader.history import collect_mtf_history_bundle, write_mtf_bundle
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
        depths = {
            "1d": args.bars_1d,
            "4h": args.bars_4h,
            "1h": args.bars_1h,
            "15m": args.bars_15m,
            "5m": args.bars_5m,
        }
        bundle = await collect_mtf_history_bundle(
            provider,
            instrument,
            bars_by_interval=depths,
            as_of=args.as_of,
            max_pages_per_interval=args.max_pages,
        )
        root = write_mtf_bundle(args.output, bundle)
        manifest = bundle.manifest
        print(json.dumps({
            "output": str(root),
            "schema_version": manifest.schema_version,
            "provider_id": manifest.provider_id,
            "symbol": manifest.canonical_symbol,
            "as_of": manifest.as_of.isoformat().replace("+00:00", "Z"),
            "candle_counts": dict(manifest.candle_counts),
            "bundle_sha256": manifest.bundle_sha256,
        }, sort_keys=True))
    finally:
        await provider.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a deep provider-recorded K-Trader MTF replay bundle")
    parser.add_argument("--provider", required=True, choices=("binance_usdm", "bybit_linear"))
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--bars-1d", type=int, default=250)
    parser.add_argument("--bars-4h", type=int, default=250)
    parser.add_argument("--bars-1h", type=int, default=250)
    parser.add_argument("--bars-15m", type=int, default=250)
    parser.add_argument("--bars-5m", type=int, default=300)
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--as-of", type=_utc)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
