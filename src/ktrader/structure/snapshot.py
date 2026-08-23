from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from collections.abc import Mapping, Sequence

from ktrader.indicators.atr import atr
from ktrader.models import NormalizedCandle
from ktrader.structure.levels import MTFLevelMap, build_mtf_level_map, cluster_swing_levels
from ktrader.structure.pivots import detect_swings
from ktrader.structure.regime import MTFRegimeSnapshot, classify_mtf_regime
from ktrader.structure.sessions import SessionContext, classify_sessions


@dataclass(frozen=True, slots=True)
class MarketStructureSnapshot:
    timestamp: datetime
    regime: MTFRegimeSnapshot
    session: SessionContext
    levels: MTFLevelMap


def build_market_structure_snapshot(
    candles_by_interval: Mapping[str, Sequence[NormalizedCandle]],
    *,
    timestamp: datetime,
    level_intervals: tuple[str, ...] = ("1d", "4h", "1h", "15m"),
    pivot_left: int = 2,
    pivot_right: int = 2,
    ma_method: str = "sma",
    volume_window: int = 20,
    min_relative_volume: Decimal = Decimal("1"),
    zone_atr_fraction: Decimal = Decimal("0.15"),
) -> MarketStructureSnapshot:
    regime = classify_mtf_regime(
        candles_by_interval,
        pivot_left=pivot_left,
        pivot_right=pivot_right,
        ma_method=ma_method,
        volume_window=volume_window,
        min_relative_volume=min_relative_volume,
    )
    session = classify_sessions(timestamp)

    levels_by_interval = {}
    for interval in level_intervals:
        candles = candles_by_interval.get(interval)
        if candles is None:
            raise ValueError(f"missing level timeframe: {interval}")
        swings = detect_swings(candles, left=pivot_left, right=pivot_right)
        levels_by_interval[interval] = cluster_swing_levels(
            swings,
            provider_id=candles[-1].provider_id,
            symbol=candles[-1].symbol,
            atr14=atr(candles, period=14),
            zone_atr_fraction=zone_atr_fraction,
        )

    return MarketStructureSnapshot(
        timestamp=timestamp,
        regime=regime,
        session=session,
        levels=build_mtf_level_map(levels_by_interval),
    )
