from __future__ import annotations

import argparse
import asyncio
from decimal import Decimal
import json
from pathlib import Path

from ktrader.history import (
    append_universe_snapshot,
    capture_universe_snapshot,
    load_universe_archive,
    write_universe_archive,
)
from ktrader.market.universe import UniverseConfig
from ktrader.providers.registry import create_provider


async def _run(args: argparse.Namespace) -> None:
    provider = create_provider(args.provider)
    try:
        config = UniverseConfig(
            quote_asset=args.quote_asset.upper(),
            price_limit_enabled=not args.all_prices,
            max_price=args.max_price,
            max_candidates=args.max_candidates,
        )
        snapshot = await capture_universe_snapshot(provider, config)
        archive = load_universe_archive(args.output) if args.output.exists() else None
        updated = append_universe_snapshot(archive, snapshot)
        target = write_universe_archive(args.output, updated)
        print(json.dumps({
            "output": str(target),
            "provider_id": snapshot.provider_id,
            "captured_at": snapshot.captured_at.isoformat().replace("+00:00", "Z"),
            "universe_size": snapshot.universe_size,
            "snapshot_sha256": snapshot.content_sha256,
            "archive_sha256": updated.archive_sha256,
            "snapshot_count": len(updated.snapshots),
        }, sort_keys=True))
    finally:
        await provider.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture one provider-native K-Trader universe/liquidity snapshot")
    parser.add_argument("--provider", required=True, choices=("binance_usdm", "bybit_linear"))
    parser.add_argument("--quote-asset", default="USDT")
    parser.add_argument("--max-price", type=Decimal, default=Decimal("3"))
    parser.add_argument("--all-prices", action="store_true")
    parser.add_argument("--max-candidates", type=int, default=50)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.max_price <= 0:
        raise SystemExit("--max-price must be positive")
    if args.max_candidates <= 0:
        raise SystemExit("--max-candidates must be positive")
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
