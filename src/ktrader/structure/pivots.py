from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from collections.abc import Sequence

from ktrader.market.validation import validate_sequence
from ktrader.models import NormalizedCandle


@dataclass(frozen=True, slots=True)
class SwingPoint:
    kind: str
    index: int
    time: datetime
    price: Decimal
    interval: str


def detect_swings(
    candles: Sequence[NormalizedCandle],
    *,
    left: int = 2,
    right: int = 2,
) -> tuple[SwingPoint, ...]:
    if left <= 0 or right <= 0:
        raise ValueError("left/right pivot windows must be positive")
    if len(candles) < left + right + 1:
        raise ValueError("insufficient candles for swing detection")

    first = candles[0]
    validate_sequence(
        candles,
        provider_id=first.provider_id,
        symbol=first.symbol,
        interval=first.interval,
        require_closed=True,
        require_contiguous=True,
    )

    result: list[SwingPoint] = []
    for index in range(left, len(candles) - right):
        candle = candles[index]
        left_slice = candles[index - left:index]
        right_slice = candles[index + 1:index + right + 1]

        if all(candle.high > other.high for other in (*left_slice, *right_slice)):
            result.append(
                SwingPoint("HIGH", index, candle.open_time, candle.high, candle.interval)
            )
        if all(candle.low < other.low for other in (*left_slice, *right_slice)):
            result.append(
                SwingPoint("LOW", index, candle.open_time, candle.low, candle.interval)
            )
    return tuple(result)


def latest_two(swings: Sequence[SwingPoint], kind: str) -> tuple[SwingPoint, SwingPoint]:
    selected = [swing for swing in swings if swing.kind == kind]
    if len(selected) < 2:
        raise ValueError(f"at least two {kind} swings are required")
    return selected[-2], selected[-1]
