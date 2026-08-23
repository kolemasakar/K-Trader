from __future__ import annotations

import argparse
import asyncio
from decimal import Decimal

from ktrader.market.service import select_first_available_provider
from ktrader.market.universe import UniverseConfig
from ktrader.providers.registry import create_provider


async def main() -> int:
    parser = argparse.ArgumentParser(description="K-Trader public provider smoke test")
    parser.add_argument(
        "--providers",
        nargs="+",
        default=["binance_usdm", "bybit_linear"],
        help="Provider priority order",
    )
    parser.add_argument("--max-price", type=Decimal, default=Decimal("3"))
    parser.add_argument("--all-prices", action="store_true")
    parser.add_argument("--max-candidates", type=int, default=20)
    args = parser.parse_args()

    providers = [create_provider(provider_id) for provider_id in args.providers]
    try:
        selection = await select_first_available_provider(
            providers,
            UniverseConfig(
                price_limit_enabled=not args.all_prices,
                max_price=args.max_price,
                max_candidates=args.max_candidates,
            ),
        )
        print(f"provider={selection.snapshot.provider_id}")
        print(f"fallback_failures={len(selection.failures)}")
        for failure in selection.failures:
            print(f"failed_provider={failure.provider_id} error={failure.error}")
        print(f"candidates={len(selection.snapshot.candidates)}")
        for candidate in selection.snapshot.candidates[:10]:
            ticker = candidate.ticker
            print(
                candidate.instrument.symbol,
                f"price={ticker.last_price}",
                f"quote_volume_24h={ticker.quote_volume_24h}",
                f"spread_bps={ticker.spread_bps}",
                f"liquidity_score={candidate.liquidity_score}",
            )
        return 0
    finally:
        for provider in providers:
            await provider.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
