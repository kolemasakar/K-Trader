from __future__ import annotations

import argparse
import asyncio
from collections.abc import Sequence

from ktrader.market.validation import validate_candle, validate_sequence
from ktrader.providers.registry import create_provider

CANONICAL_INTERVALS = ("5m", "15m", "1h", "4h", "1d")


async def check_provider(provider_id: str, *, symbol: str, ws_timeout: float) -> str:
    provider = create_provider(provider_id)
    stream = None
    try:
        instruments = await provider.list_instruments()
        eligible = [item for item in instruments if item.is_tradable_perpetual]
        if not eligible:
            raise RuntimeError("no tradable perpetual instruments")
        instrument = next((item for item in eligible if item.symbol == symbol), eligible[0])

        for interval in CANONICAL_INTERVALS:
            provider.validate_interval(interval)
            raw = await provider.get_candles(instrument, interval, limit=8)
            closed = [candle for candle in raw if candle.closed]
            if len(closed) < 5:
                raise RuntimeError(f"insufficient closed {interval} candles")
            selected = closed[-5:]
            validate_sequence(
                selected,
                provider_id=provider.provider_id,
                symbol=instrument.symbol,
                interval=interval,
                require_closed=True,
                require_contiguous=True,
            )

        stream = provider.stream_candles([instrument], "5m")
        event = await asyncio.wait_for(anext(stream), timeout=ws_timeout)
        validate_candle(
            event.candle,
            provider_id=provider.provider_id,
            symbol=instrument.symbol,
            interval="5m",
        )
        return instrument.symbol
    finally:
        if stream is not None:
            await stream.aclose()
        await provider.close()


async def run(providers: Sequence[str], *, symbol: str, ws_timeout: float) -> int:
    failures: list[str] = []
    for provider_id in providers:
        try:
            selected_symbol = await check_provider(
                provider_id,
                symbol=symbol,
                ws_timeout=ws_timeout,
            )
        except Exception as exc:
            detail = f"{provider_id}: {type(exc).__name__}: {exc}"
            failures.append(detail)
            print(f"FAIL {detail}")
            continue
        print(
            "PASS "
            f"provider={provider_id} symbol={selected_symbol} "
            "rest_intervals=5m,15m,1h,4h,1d websocket=5m"
        )
        if failures:
            print(f"fallback_failures={len(failures)}")
        return 0

    print("FAIL no public provider passed VPS acceptance")
    for detail in failures:
        print(f"provider_failure={detail}")
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="K-Trader target-VPS public REST/WebSocket acceptance"
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        default=["binance_usdm", "bybit_linear"],
        help="Provider priority order",
    )
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--ws-timeout", type=float, default=90.0)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(
        asyncio.run(
            run(
                args.providers,
                symbol=args.symbol,
                ws_timeout=args.ws_timeout,
            )
        )
    )
