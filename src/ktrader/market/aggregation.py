from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from ktrader.market.timeframes import (
    datetime_from_ms,
    datetime_to_ms,
    expected_close_time,
    interval_ms,
)
from ktrader.market.validation import CandleValidationError, validate_sequence
from ktrader.models import NormalizedCandle

PARENT_INTERVALS = ("15m", "1h", "4h", "1d")


def bucket_open_time(value: datetime, interval: str) -> datetime:
    size = interval_ms(interval)
    return datetime_from_ms((datetime_to_ms(value) // size) * size)


def expected_child_count(parent_interval: str, child_interval: str = "5m") -> int:
    parent = interval_ms(parent_interval)
    child = interval_ms(child_interval)
    if parent % child != 0:
        raise ValueError("parent interval must be an integer multiple of child interval")
    return parent // child


def aggregate_closed_candles(
    candles: Sequence[NormalizedCandle],
    *,
    parent_interval: str,
    child_interval: str = "5m",
) -> NormalizedCandle:
    required = expected_child_count(parent_interval, child_interval)
    if len(candles) != required:
        raise CandleValidationError(
            f"Incomplete {parent_interval} bucket: "
            f"required={required}, received={len(candles)}"
        )
    first = candles[0]
    validate_sequence(
        candles,
        provider_id=first.provider_id,
        symbol=first.symbol,
        interval=child_interval,
        require_closed=True,
        require_contiguous=True,
    )
    bucket = bucket_open_time(first.open_time, parent_interval)
    if first.open_time != bucket:
        raise CandleValidationError(
            "Child sequence does not start at parent UTC boundary"
        )
    expected_last_open_ms = (
        datetime_to_ms(bucket)
        + interval_ms(parent_interval)
        - interval_ms(child_interval)
    )
    if datetime_to_ms(candles[-1].open_time) != expected_last_open_ms:
        raise CandleValidationError(
            "Child sequence does not complete parent interval"
        )

    return NormalizedCandle(
        provider_id=first.provider_id,
        symbol=first.symbol,
        interval=parent_interval,
        open_time=bucket,
        close_time=expected_close_time(bucket, parent_interval),
        open=first.open,
        high=max(c.high for c in candles),
        low=min(c.low for c in candles),
        close=candles[-1].close,
        volume=sum((c.volume for c in candles), Decimal("0")),
        quote_volume=_sum_optional(c.quote_volume for c in candles),
        trade_count=_sum_optional_int(c.trade_count for c in candles),
        taker_buy_volume=_sum_optional(c.taker_buy_volume for c in candles),
        taker_buy_quote_volume=_sum_optional(
            c.taker_buy_quote_volume for c in candles
        ),
        closed=True,
    )


def _sum_optional(values):
    items = list(values)
    if any(value is None for value in items):
        return None
    return sum(items, Decimal("0"))


def _sum_optional_int(values):
    items = list(values)
    if any(value is None for value in items):
        return None
    return sum(items)
