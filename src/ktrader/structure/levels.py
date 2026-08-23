from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from collections.abc import Mapping, Sequence

from ktrader.market.validation import validate_candle
from ktrader.models import NormalizedCandle
from ktrader.structure.pivots import SwingPoint


LEVEL_TYPES = {
    "TREND_BREAK",
    "HISTORICAL",
    "MIRROR",
    "LIMIT",
    "PARANORMAL_BAR",
    "CONSOLIDATION",
}
LEVEL_SIDES = {"SUPPORT", "RESISTANCE", "ZONE"}
LEVEL_STATUSES = {"FLOATING", "CONFIRMED", "BROKEN", "MIRROR", "INVALIDATED"}

TIMEFRAME_PRIORITY = {
    "1d": 5,
    "4h": 4,
    "1h": 3,
    "15m": 2,
    "5m": 1,
}


@dataclass(frozen=True, slots=True)
class PriceLevel:
    level_id: str
    provider_id: str
    symbol: str
    timeframe: str
    lower: Decimal
    upper: Decimal
    side: str
    status: str
    types: tuple[str, ...]
    touches: int
    strength: str
    created_at: datetime
    last_test: datetime | None = None
    break_time: datetime | None = None
    invalidation_reason: str | None = None

    @property
    def confirmed(self) -> bool:
        return self.status in {"CONFIRMED", "BROKEN", "MIRROR"}

    @property
    def invalidated(self) -> bool:
        return self.status == "INVALIDATED"

    @property
    def midpoint(self) -> Decimal:
        return (self.lower + self.upper) / Decimal("2")


@dataclass(frozen=True, slots=True)
class MTFLevelMap:
    levels: tuple[PriceLevel, ...]

    def active(self, *, confirmed_only: bool = True) -> tuple[PriceLevel, ...]:
        result = [
            level
            for level in self.levels
            if level.status in {"FLOATING", "CONFIRMED", "MIRROR"}
        ]
        if confirmed_only:
            result = [
                level
                for level in result
                if level.status in {"CONFIRMED", "MIRROR"}
            ]
        return tuple(result)

    def nearest_support(self, price: Decimal) -> PriceLevel | None:
        candidates = [
            level
            for level in self.active()
            if level.side == "SUPPORT" and level.midpoint <= price
        ]
        return max(candidates, key=lambda level: level.midpoint, default=None)

    def nearest_resistance(self, price: Decimal) -> PriceLevel | None:
        candidates = [
            level
            for level in self.active()
            if level.side == "RESISTANCE" and level.midpoint >= price
        ]
        return min(candidates, key=lambda level: level.midpoint, default=None)


def strength_from_touches(touches: int) -> str:
    if touches <= 0:
        raise ValueError("touches must be positive")
    if touches == 1:
        return "WEAK"
    if touches == 2:
        return "MODERATE"
    return "STRONG"


def _level_id(
    provider_id: str,
    symbol: str,
    timeframe: str,
    side: str,
    created_at: datetime,
    midpoint: Decimal,
) -> str:
    price_token = format(midpoint.normalize(), "f").replace(".", "_")
    return (
        f"{provider_id}:{symbol}:{timeframe}:{side}:"
        f"{int(created_at.timestamp())}:{price_token}"
    )


def cluster_swing_levels(
    swings: Sequence[SwingPoint],
    *,
    provider_id: str,
    symbol: str,
    atr14: Decimal,
    zone_atr_fraction: Decimal = Decimal("0.15"),
    confirm_touches: int = 2,
) -> tuple[PriceLevel, ...]:
    if atr14 <= 0 or zone_atr_fraction <= 0:
        raise ValueError("ATR14 and zone_atr_fraction must be positive")
    if confirm_touches < 2:
        raise ValueError("confirm_touches must be >= 2")
    if not swings:
        return ()

    radius = atr14 * zone_atr_fraction
    grouped: list[list[SwingPoint]] = []

    for swing in sorted(swings, key=lambda item: (item.kind, item.price, item.time)):
        matched = None
        for cluster in grouped:
            if cluster[0].kind != swing.kind:
                continue
            center = sum((item.price for item in cluster), Decimal("0")) / Decimal(
                len(cluster)
            )
            if abs(swing.price - center) <= radius:
                matched = cluster
                break
        if matched is None:
            grouped.append([swing])
        else:
            matched.append(swing)

    levels: list[PriceLevel] = []
    for cluster in grouped:
        touches = len(cluster)
        center = sum((item.price for item in cluster), Decimal("0")) / Decimal(
            touches
        )
        side = "RESISTANCE" if cluster[0].kind == "HIGH" else "SUPPORT"
        status = "CONFIRMED" if touches >= confirm_touches else "FLOATING"
        created_at = min(item.time for item in cluster)
        levels.append(
            PriceLevel(
                level_id=_level_id(
                    provider_id,
                    symbol,
                    cluster[0].interval,
                    side,
                    created_at,
                    center,
                ),
                provider_id=provider_id,
                symbol=symbol,
                timeframe=cluster[0].interval,
                lower=min(item.price for item in cluster) - radius,
                upper=max(item.price for item in cluster) + radius,
                side=side,
                status=status,
                types=("HISTORICAL",),
                touches=touches,
                strength=strength_from_touches(touches),
                created_at=created_at,
                last_test=max(item.time for item in cluster),
            )
        )
    return tuple(levels)


def explicit_level(
    *,
    provider_id: str,
    symbol: str,
    timeframe: str,
    lower: Decimal,
    upper: Decimal,
    side: str,
    level_type: str,
    created_at: datetime,
    confirmed: bool = False,
    touches: int = 1,
) -> PriceLevel:
    if level_type not in LEVEL_TYPES:
        raise ValueError(f"unsupported level type: {level_type}")
    if side not in LEVEL_SIDES:
        raise ValueError(f"unsupported level side: {side}")
    if lower > upper:
        raise ValueError("lower cannot exceed upper")
    midpoint = (lower + upper) / Decimal("2")
    normalized_touches = max(touches, 1)
    return PriceLevel(
        level_id=_level_id(
            provider_id,
            symbol,
            timeframe,
            side,
            created_at,
            midpoint,
        ),
        provider_id=provider_id,
        symbol=symbol,
        timeframe=timeframe,
        lower=lower,
        upper=upper,
        side=side,
        status="CONFIRMED" if confirmed else "FLOATING",
        types=(level_type,),
        touches=normalized_touches,
        strength=strength_from_touches(normalized_touches),
        created_at=created_at,
    )


def update_level(
    level: PriceLevel,
    candle: NormalizedCandle,
    *,
    break_buffer: Decimal = Decimal("0"),
) -> PriceLevel:
    validate_candle(candle, provider_id=level.provider_id, symbol=level.symbol)
    if not candle.closed:
        raise ValueError("level lifecycle requires a closed candle")
    if break_buffer < 0:
        raise ValueError("break_buffer cannot be negative")
    if level.invalidated or level.status == "FLOATING":
        return level

    if level.status == "CONFIRMED":
        broken = (
            level.side == "SUPPORT" and candle.close < level.lower - break_buffer
        ) or (
            level.side == "RESISTANCE" and candle.close > level.upper + break_buffer
        )
        if broken:
            types = tuple(dict.fromkeys((*level.types, "TREND_BREAK")))
            return replace(
                level,
                status="BROKEN",
                types=types,
                break_time=candle.close_time,
                last_test=candle.close_time,
            )
        return level

    if level.status == "BROKEN":
        if level.side == "SUPPORT":
            retest = candle.high >= level.lower and candle.close < level.lower
            if retest:
                return replace(
                    level,
                    side="RESISTANCE",
                    status="MIRROR",
                    types=tuple(dict.fromkeys((*level.types, "MIRROR"))),
                    last_test=candle.close_time,
                )
        elif level.side == "RESISTANCE":
            retest = candle.low <= level.upper and candle.close > level.upper
            if retest:
                return replace(
                    level,
                    side="SUPPORT",
                    status="MIRROR",
                    types=tuple(dict.fromkeys((*level.types, "MIRROR"))),
                    last_test=candle.close_time,
                )
        return level

    if level.status == "MIRROR":
        invalid = (
            level.side == "SUPPORT" and candle.close < level.lower - break_buffer
        ) or (
            level.side == "RESISTANCE" and candle.close > level.upper + break_buffer
        )
        if invalid:
            return replace(
                level,
                status="INVALIDATED",
                invalidation_reason="MIRROR_FAILED",
                last_test=candle.close_time,
            )
    return level


def build_mtf_level_map(
    levels_by_interval: Mapping[str, Sequence[PriceLevel]],
) -> MTFLevelMap:
    flattened: list[PriceLevel] = []
    for interval, levels in levels_by_interval.items():
        for level in levels:
            if level.timeframe != interval:
                raise ValueError("level timeframe does not match MTF map key")
            flattened.append(level)

    rank = {"STRONG": 3, "MODERATE": 2, "WEAK": 1}
    flattened.sort(
        key=lambda level: (
            -TIMEFRAME_PRIORITY.get(level.timeframe, 0),
            -rank[level.strength],
            level.midpoint,
        )
    )
    return MTFLevelMap(tuple(flattened))
