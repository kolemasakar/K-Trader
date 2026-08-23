from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from collections.abc import Sequence

from ktrader.models import NormalizedCandle
from ktrader.indicators.atr import atr
from ktrader.indicators.moving_average import ma50_200
from ktrader.indicators.volume import VolumeStats, latest_volume_stats


@dataclass(frozen=True, slots=True)
class IndicatorSnapshot:
    provider_id: str
    symbol: str
    interval: str
    data_time: datetime
    close: Decimal
    atr14: Decimal
    ma_method: str
    ma50: Decimal
    ma200: Decimal
    volume: VolumeStats


def build_indicator_snapshot(
    candles: Sequence[NormalizedCandle],
    *,
    ma_method: str = "sma",
    volume_window: int = 20,
) -> IndicatorSnapshot:
    if not candles:
        raise ValueError("candle sequence is empty")
    latest = candles[-1]
    ma = ma50_200(candles, method=ma_method)
    return IndicatorSnapshot(
        provider_id=latest.provider_id,
        symbol=latest.symbol,
        interval=latest.interval,
        data_time=latest.close_time,
        close=latest.close,
        atr14=atr(candles, period=14),
        ma_method=ma.method,
        ma50=ma.ma50,
        ma200=ma.ma200,
        volume=latest_volume_stats(candles, window=volume_window),
    )
