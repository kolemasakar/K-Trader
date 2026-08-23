from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from collections.abc import Sequence

from ktrader.models import NormalizedCandle
from ktrader.market.timeframes import (
    datetime_to_ms,
    expected_close_time,
    interval_ms,
    interval_seconds,
    is_aligned_open,
    require_utc,
)


class CandleValidationError(ValueError):
    """Normalized candle or candle-series integrity violation."""


@dataclass(frozen=True, slots=True)
class CandleGap:
    after_open_time: datetime
    before_open_time: datetime
    missing_count: int


@dataclass(frozen=True, slots=True)
class FreshnessResult:
    interval: str
    latest_close_time: datetime
    age_seconds: float
    max_age_seconds: float
    stale: bool


@dataclass(frozen=True, slots=True)
class FreshnessPolicy:
    max_age_intervals: float = 2.0

    def max_age_seconds(self, interval: str) -> float:
        if self.max_age_intervals <= 0:
            raise ValueError("max_age_intervals must be positive")
        return interval_seconds(interval) * self.max_age_intervals


def validate_candle(
    candle: NormalizedCandle,
    *,
    provider_id: str | None = None,
    symbol: str | None = None,
    interval: str | None = None,
) -> None:
    expected_interval = interval or candle.interval
    if provider_id is not None and candle.provider_id != provider_id:
        raise CandleValidationError("Candle provider_id does not match snapshot provider")
    if symbol is not None and candle.symbol != symbol:
        raise CandleValidationError("Candle symbol does not match snapshot instrument")
    if candle.interval != expected_interval:
        raise CandleValidationError("Candle interval does not match requested interval")

    try:
        require_utc(candle.open_time)
        require_utc(candle.close_time)
    except ValueError as exc:
        raise CandleValidationError(str(exc)) from exc

    if not is_aligned_open(candle.open_time, expected_interval):
        raise CandleValidationError("Candle open_time is not aligned to UTC interval boundary")
    if candle.close_time != expected_close_time(candle.open_time, expected_interval):
        raise CandleValidationError("Candle close_time does not match normalized interval boundary")

    prices = (candle.open, candle.high, candle.low, candle.close)
    if any(not value.is_finite() or value <= 0 for value in prices):
        raise CandleValidationError("OHLC values must be finite and positive")
    if candle.low > min(candle.open, candle.close):
        raise CandleValidationError("Candle low exceeds open/close")
    if candle.high < max(candle.open, candle.close):
        raise CandleValidationError("Candle high is below open/close")
    if candle.low > candle.high:
        raise CandleValidationError("Candle low exceeds high")

    _validate_nonnegative(candle.volume, "volume")
    if candle.quote_volume is not None:
        _validate_nonnegative(candle.quote_volume, "quote_volume")
    if candle.taker_buy_volume is not None:
        _validate_nonnegative(candle.taker_buy_volume, "taker_buy_volume")
    if candle.taker_buy_quote_volume is not None:
        _validate_nonnegative(candle.taker_buy_quote_volume, "taker_buy_quote_volume")
    if candle.trade_count is not None and candle.trade_count < 0:
        raise CandleValidationError("trade_count must be nonnegative")


def validate_sequence(
    candles: Sequence[NormalizedCandle],
    *,
    provider_id: str,
    symbol: str,
    interval: str,
    require_closed: bool = True,
    require_contiguous: bool = True,
) -> tuple[CandleGap, ...]:
    if not candles:
        raise CandleValidationError("Candle sequence is empty")

    previous_open: datetime | None = None
    for candle in candles:
        validate_candle(candle, provider_id=provider_id, symbol=symbol, interval=interval)
        if require_closed and not candle.closed:
            raise CandleValidationError("Bootstrap snapshot contains an open candle")
        if previous_open is not None and candle.open_time <= previous_open:
            raise CandleValidationError("Candle sequence is not strictly chronological")
        previous_open = candle.open_time

    gaps = find_gaps(candles, interval)
    if require_contiguous and gaps:
        raise CandleValidationError(
            "Candle sequence contains missing bars: "
            + ", ".join(str(gap.missing_count) for gap in gaps)
        )
    return gaps


def find_gaps(candles: Sequence[NormalizedCandle], interval: str) -> tuple[CandleGap, ...]:
    if len(candles) < 2:
        return ()
    step = interval_ms(interval)
    gaps: list[CandleGap] = []
    for left, right in zip(candles, candles[1:]):
        delta = datetime_to_ms(right.open_time) - datetime_to_ms(left.open_time)
        if delta == step:
            continue
        if delta <= 0 or delta % step != 0:
            raise CandleValidationError("Candle sequence has invalid interval spacing")
        gaps.append(
            CandleGap(
                after_open_time=left.open_time,
                before_open_time=right.open_time,
                missing_count=(delta // step) - 1,
            )
        )
    return tuple(gaps)


def assess_freshness(
    latest: NormalizedCandle,
    *,
    policy: FreshnessPolicy,
    now: datetime | None = None,
) -> FreshnessResult:
    if not latest.closed:
        raise CandleValidationError("Freshness must be assessed from a closed candle")
    current = now or datetime.now(timezone.utc)
    try:
        require_utc(current)
    except ValueError as exc:
        raise CandleValidationError(str(exc)) from exc
    age_seconds = max(0.0, (current - latest.close_time).total_seconds())
    max_age_seconds = policy.max_age_seconds(latest.interval)
    return FreshnessResult(
        interval=latest.interval,
        latest_close_time=latest.close_time,
        age_seconds=age_seconds,
        max_age_seconds=max_age_seconds,
        stale=age_seconds > max_age_seconds,
    )


def _validate_nonnegative(value: Decimal, name: str) -> None:
    if not value.is_finite() or value < 0:
        raise CandleValidationError(f"{name} must be finite and nonnegative")
