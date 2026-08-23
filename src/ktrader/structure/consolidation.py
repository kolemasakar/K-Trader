from __future__ import annotations

from decimal import Decimal
from collections.abc import Sequence

from ktrader.indicators.atr import atr
from ktrader.models import NormalizedCandle
from ktrader.structure.levels import PriceLevel, explicit_level


def detect_consolidation_level(
    candles: Sequence[NormalizedCandle],
    *,
    window: int = 12,
    max_width_atr: Decimal = Decimal("2"),
) -> PriceLevel | None:
    if window < 3:
        raise ValueError("window must be >= 3")
    if max_width_atr <= 0:
        raise ValueError("max_width_atr must be positive")
    if len(candles) < max(window, 14):
        raise ValueError("insufficient candles for consolidation detection")

    recent = candles[-window:]
    width = max(candle.high for candle in recent) - min(candle.low for candle in recent)
    reference_atr = atr(candles, period=14)
    if width > max_width_atr * reference_atr:
        return None

    first = recent[0]
    return explicit_level(
        provider_id=first.provider_id,
        symbol=first.symbol,
        timeframe=first.interval,
        lower=min(candle.low for candle in recent),
        upper=max(candle.high for candle in recent),
        side="ZONE",
        level_type="CONSOLIDATION",
        created_at=first.open_time,
        confirmed=True,
        touches=3,
    )
