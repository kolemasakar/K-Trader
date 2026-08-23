from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from collections.abc import Sequence

from ktrader.models import NormalizedCandle
from ktrader.market.validation import validate_sequence


@dataclass(frozen=True, slots=True)
class VolumeStats:
    window: int
    volume: Decimal
    average_volume: Decimal
    relative_volume: Decimal
    spread: Decimal
    average_spread: Decimal
    relative_spread: Decimal
    quote_volume: Decimal | None
    average_quote_volume: Decimal | None
    relative_quote_volume: Decimal | None


def latest_volume_stats(
    candles: Sequence[NormalizedCandle],
    *,
    window: int = 20,
) -> VolumeStats:
    if window <= 0:
        raise ValueError("window must be positive")
    if len(candles) < window + 1:
        raise ValueError(f"at least {window + 1} closed candles are required")
    first = candles[0]
    validate_sequence(
        candles,
        provider_id=first.provider_id,
        symbol=first.symbol,
        interval=first.interval,
        require_closed=True,
        require_contiguous=True,
    )
    current = candles[-1]
    baseline = candles[-(window + 1):-1]

    average_volume = sum((candle.volume for candle in baseline), Decimal("0")) / Decimal(window)
    if average_volume <= 0:
        raise ValueError("average volume baseline must be positive")

    spread = current.high - current.low
    average_spread = sum(
        (candle.high - candle.low for candle in baseline), Decimal("0")
    ) / Decimal(window)
    if average_spread <= 0:
        raise ValueError("average spread baseline must be positive")

    quote_values = [candle.quote_volume for candle in baseline]
    average_quote_volume: Decimal | None = None
    relative_quote_volume: Decimal | None = None
    if current.quote_volume is not None and all(value is not None for value in quote_values):
        average_quote_volume = sum(
            (value for value in quote_values if value is not None), Decimal("0")
        ) / Decimal(window)
        if average_quote_volume > 0:
            relative_quote_volume = current.quote_volume / average_quote_volume

    return VolumeStats(
        window=window,
        volume=current.volume,
        average_volume=average_volume,
        relative_volume=current.volume / average_volume,
        spread=spread,
        average_spread=average_spread,
        relative_spread=spread / average_spread,
        quote_volume=current.quote_volume,
        average_quote_volume=average_quote_volume,
        relative_quote_volume=relative_quote_volume,
    )
