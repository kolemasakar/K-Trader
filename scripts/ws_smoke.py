from __future__ import annotations

import argparse
import asyncio

from ktrader.providers import BinanceUSDMProvider, BybitLinearProvider


def _provider(name: str):
    if name == "binance_usdm":
        return BinanceUSDMProvider()
    if name == "bybit_linear":
        return BybitLinearProvider()
    raise ValueError(f"Unsupported provider: {name}")


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="K-Trader public WebSocket smoke test"
    )
    parser.add_argument(
        "--provider",
        choices=("binance_usdm", "bybit_linear"),
        required=True,
    )
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    provider = _provider(args.provider)
    stream = None
    try:
        instruments = await provider.list_instruments()
        instrument = next(
            item
            for item in instruments
            if item.symbol == args.symbol and item.is_tradable_perpetual
        )
        stream = provider.stream_candles([instrument], "5m")
        event = await asyncio.wait_for(anext(stream), timeout=args.timeout)
        candle = event.candle
        print(
            "PASS "
            f"provider={provider.provider_id} "
            f"symbol={candle.symbol} "
            f"interval={candle.interval} "
            f"closed={candle.closed} "
            f"open_time={candle.open_time.isoformat()} "
            f"received_at={event.received_at.isoformat()}"
        )
    finally:
        if stream is not None:
            await stream.aclose()
        await provider.close()


if __name__ == "__main__":
    asyncio.run(main())
