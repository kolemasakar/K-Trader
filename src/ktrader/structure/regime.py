from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from collections.abc import Mapping, Sequence

from ktrader.indicators.moving_average import ma50_200
from ktrader.indicators.volume import latest_volume_stats
from ktrader.models import NormalizedCandle
from ktrader.structure.pivots import SwingPoint, detect_swings, latest_two


DIRECTIONAL = {"BULLISH", "BEARISH"}


@dataclass(frozen=True, slots=True)
class RegimeSnapshot:
    interval: str
    structure_direction: str
    ma_direction: str
    regime: str
    latest_highs: tuple[SwingPoint, SwingPoint]
    latest_lows: tuple[SwingPoint, SwingPoint]


@dataclass(frozen=True, slots=True)
class StrengthSnapshot:
    interval: str
    direction: str
    evidence_count: int
    classification: str
    evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MTFRegimeSnapshot:
    regime: str
    by_interval: Mapping[str, RegimeSnapshot]
    strength_by_interval: Mapping[str, StrengthSnapshot]


def _structure_direction(
    swings: Sequence[SwingPoint],
) -> tuple[str, tuple[SwingPoint, SwingPoint], tuple[SwingPoint, SwingPoint]]:
    highs = latest_two(swings, "HIGH")
    lows = latest_two(swings, "LOW")
    if highs[1].price > highs[0].price and lows[1].price > lows[0].price:
        direction = "BULLISH"
    elif highs[1].price < highs[0].price and lows[1].price < lows[0].price:
        direction = "BEARISH"
    else:
        direction = "RANGE_OR_TRANSITION"
    return direction, highs, lows


def _ma_direction(candles: Sequence[NormalizedCandle], method: str) -> str:
    ma = ma50_200(candles, method=method)
    if ma.close > ma.ma50 > ma.ma200:
        return "BULLISH"
    if ma.close < ma.ma50 < ma.ma200:
        return "BEARISH"
    return "NEUTRAL"


def classify_regime(
    candles: Sequence[NormalizedCandle],
    *,
    pivot_left: int = 2,
    pivot_right: int = 2,
    ma_method: str = "sma",
) -> RegimeSnapshot:
    swings = detect_swings(candles, left=pivot_left, right=pivot_right)
    structure, highs, lows = _structure_direction(swings)
    ma_direction = _ma_direction(candles, ma_method)

    if structure == ma_direction and structure in DIRECTIONAL:
        regime = structure
    elif structure == "RANGE_OR_TRANSITION" and ma_direction == "NEUTRAL":
        regime = "RANGE"
    else:
        regime = "MIXED"

    return RegimeSnapshot(
        interval=candles[-1].interval,
        structure_direction=structure,
        ma_direction=ma_direction,
        regime=regime,
        latest_highs=highs,
        latest_lows=lows,
    )


def classify_strength(
    candles: Sequence[NormalizedCandle],
    regime: RegimeSnapshot,
    *,
    volume_window: int = 20,
    min_relative_volume: Decimal = Decimal("1"),
) -> StrengthSnapshot:
    if regime.regime not in DIRECTIONAL:
        return StrengthSnapshot(
            interval=regime.interval,
            direction=regime.regime,
            evidence_count=0,
            classification="NEUTRAL" if regime.regime == "RANGE" else "WEAK",
            evidence=(),
        )

    if min_relative_volume <= 0:
        raise ValueError("min_relative_volume must be positive")

    evidence: list[str] = []
    if regime.structure_direction == regime.regime:
        evidence.append("STRUCTURE")
    if regime.ma_direction == regime.regime:
        evidence.append("MA_ALIGNMENT")

    volume = latest_volume_stats(candles, window=volume_window)
    if volume.relative_volume >= min_relative_volume:
        evidence.append("PARTICIPATION")

    count = len(evidence)
    classification = "STRONG" if count == 3 else "MODERATE" if count == 2 else "WEAK"
    return StrengthSnapshot(
        interval=regime.interval,
        direction=regime.regime,
        evidence_count=count,
        classification=classification,
        evidence=tuple(evidence),
    )


def classify_mtf_regime(
    candles_by_interval: Mapping[str, Sequence[NormalizedCandle]],
    *,
    timeframes: tuple[str, str, str] = ("1d", "4h", "1h"),
    pivot_left: int = 2,
    pivot_right: int = 2,
    ma_method: str = "sma",
    volume_window: int = 20,
    min_relative_volume: Decimal = Decimal("1"),
) -> MTFRegimeSnapshot:
    missing = [interval for interval in timeframes if interval not in candles_by_interval]
    if missing:
        raise ValueError(f"missing required HTF intervals: {', '.join(missing)}")

    regimes: dict[str, RegimeSnapshot] = {}
    strengths: dict[str, StrengthSnapshot] = {}
    for interval in timeframes:
        snapshot = classify_regime(
            candles_by_interval[interval],
            pivot_left=pivot_left,
            pivot_right=pivot_right,
            ma_method=ma_method,
        )
        regimes[interval] = snapshot
        strengths[interval] = classify_strength(
            candles_by_interval[interval],
            snapshot,
            volume_window=volume_window,
            min_relative_volume=min_relative_volume,
        )

    d1, h4, h1 = (regimes[tf].regime for tf in timeframes)
    if d1 in DIRECTIONAL and h4 == d1:
        combined = d1
    elif d1 not in DIRECTIONAL and h4 in DIRECTIONAL and h1 == h4:
        combined = h4
    elif all(value == "RANGE" for value in (d1, h4, h1)):
        combined = "RANGE"
    else:
        combined = "MIXED"

    return MTFRegimeSnapshot(combined, regimes, strengths)
