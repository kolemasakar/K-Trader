from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from collections.abc import Sequence

from ktrader.models import NormalizedCandle
from ktrader.market.validation import validate_sequence


@dataclass(frozen=True, slots=True)
class ATR5DResult:
    atr5d: Decimal
    reference_atr14: Decimal
    valid_ranges: tuple[Decimal, ...]
    valid_open_times: tuple[datetime, ...]
    rejected_high: int
    rejected_low: int


def _require_closed_contiguous(candles: Sequence[NormalizedCandle]) -> None:
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


def true_range(candle: NormalizedCandle, previous_close: Decimal | None = None) -> Decimal:
    high_low = candle.high - candle.low
    if previous_close is None:
        return high_low
    return max(
        high_low,
        abs(candle.high - previous_close),
        abs(candle.low - previous_close),
    )


def wilder_atr_series(
    candles: Sequence[NormalizedCandle],
    *,
    period: int = 14,
) -> tuple[Decimal | None, ...]:
    if period <= 0:
        raise ValueError("period must be positive")
    _require_closed_contiguous(candles)
    if len(candles) < period:
        return tuple(None for _ in candles)

    trs: list[Decimal] = []
    previous_close: Decimal | None = None
    for candle in candles:
        trs.append(true_range(candle, previous_close))
        previous_close = candle.close

    result: list[Decimal | None] = [None] * len(candles)
    atr_value = sum(trs[:period], Decimal("0")) / Decimal(period)
    result[period - 1] = atr_value
    divisor = Decimal(period)
    multiplier = Decimal(period - 1)
    for index in range(period, len(candles)):
        atr_value = ((atr_value * multiplier) + trs[index]) / divisor
        result[index] = atr_value
    return tuple(result)


def atr(
    candles: Sequence[NormalizedCandle],
    *,
    period: int = 14,
) -> Decimal:
    series = wilder_atr_series(candles, period=period)
    latest = series[-1]
    if latest is None:
        raise ValueError(f"at least {period} closed candles are required for ATR{period}")
    return latest


def atr5d(
    d1_candles: Sequence[NormalizedCandle],
    *,
    atr_period: int = 14,
    valid_count: int = 5,
    high_multiplier: Decimal = Decimal("2"),
    low_multiplier: Decimal = Decimal("0.3333333333333333333333333333"),
) -> ATR5DResult:
    if valid_count <= 0:
        raise ValueError("valid_count must be positive")
    _require_closed_contiguous(d1_candles)
    if d1_candles[0].interval != "1d":
        raise ValueError("ATR5D requires canonical 1d candles")
    atr_series = wilder_atr_series(d1_candles, period=atr_period)

    selected_ranges: list[Decimal] = []
    selected_times: list[datetime] = []
    rejected_high = 0
    rejected_low = 0
    latest_reference: Decimal | None = None

    for index in range(len(d1_candles) - 1, -1, -1):
        reference = atr_series[index]
        if reference is None:
            continue
        if latest_reference is None:
            latest_reference = reference
        candle_range = d1_candles[index].high - d1_candles[index].low
        if candle_range >= high_multiplier * reference:
            rejected_high += 1
            continue
        if candle_range <= low_multiplier * reference:
            rejected_low += 1
            continue
        selected_ranges.append(candle_range)
        selected_times.append(d1_candles[index].open_time)
        if len(selected_ranges) == valid_count:
            break

    if len(selected_ranges) < valid_count or latest_reference is None:
        raise ValueError(
            f"ATR5D requires {valid_count} valid 1d bars after abnormal-range filtering"
        )

    return ATR5DResult(
        atr5d=sum(selected_ranges, Decimal("0")) / Decimal(valid_count),
        reference_atr14=latest_reference,
        valid_ranges=tuple(selected_ranges),
        valid_open_times=tuple(selected_times),
        rejected_high=rejected_high,
        rejected_low=rejected_low,
    )
