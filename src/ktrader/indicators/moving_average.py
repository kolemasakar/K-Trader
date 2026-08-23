from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from collections.abc import Sequence

from ktrader.models import NormalizedCandle
from ktrader.market.validation import validate_sequence


@dataclass(frozen=True, slots=True)
class MASnapshot:
    method: str
    close: Decimal
    ma50: Decimal
    ma200: Decimal


def _validate(candles: Sequence[NormalizedCandle]) -> None:
    if not candles:
        raise ValueError("candle sequence is empty")
    first = candles[0]
    validate_sequence(
        candles,
        provider_id=first.provider_id,
        symbol=first.symbol,
        interval=first.interval,
        require_closed=True,
        require_contiguous=True,
    )


def sma(values: Sequence[Decimal], *, period: int) -> Decimal:
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) < period:
        raise ValueError(f"at least {period} values are required")
    return sum(values[-period:], Decimal("0")) / Decimal(period)


def ema(values: Sequence[Decimal], *, period: int) -> Decimal:
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) < period:
        raise ValueError(f"at least {period} values are required")
    value = sum(values[:period], Decimal("0")) / Decimal(period)
    alpha = Decimal("2") / Decimal(period + 1)
    for current in values[period:]:
        value = (current * alpha) + (value * (Decimal("1") - alpha))
    return value


def moving_average(
    candles: Sequence[NormalizedCandle],
    *,
    period: int,
    method: str = "sma",
) -> Decimal:
    _validate(candles)
    values = [candle.close for candle in candles]
    normalized = method.lower()
    if normalized == "sma":
        return sma(values, period=period)
    if normalized == "ema":
        return ema(values, period=period)
    raise ValueError("method must be 'sma' or 'ema'")


def ma50_200(
    candles: Sequence[NormalizedCandle],
    *,
    method: str = "sma",
) -> MASnapshot:
    _validate(candles)
    return MASnapshot(
        method=method.lower(),
        close=candles[-1].close,
        ma50=moving_average(candles, period=50, method=method),
        ma200=moving_average(candles, period=200, method=method),
    )
