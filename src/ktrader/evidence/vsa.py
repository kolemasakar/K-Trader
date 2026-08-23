from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from collections.abc import Sequence

from ktrader.market.validation import validate_sequence
from ktrader.models import NormalizedCandle
from ktrader.structure.levels import MTFLevelMap, PriceLevel
from ktrader.structure.regime import MTFRegimeSnapshot
from ktrader.evidence.trap import TrapEvent


BULLISH_VSA = {"NS", "T", "SC", "SV"}
BEARISH_VSA = {"ND", "UT", "BC"}


@dataclass(frozen=True, slots=True)
class VSAEvent:
    event_type: str
    provider_id: str
    symbol: str
    timeframe: str
    bar_index: int
    bar_time: datetime
    direction: str
    relative_volume: Decimal
    relative_spread: Decimal
    close_location: Decimal
    raw_quality: str
    context_status: str = "RAW"
    confirmed: bool = False
    reference_level_id: str | None = None
    trap_confirmed: bool = False
    reasons: tuple[str, ...] = ()
    invalidation_reason: str | None = None


def _close_location(candle: NormalizedCandle) -> Decimal:
    spread = candle.high - candle.low
    if spread <= 0:
        return Decimal("0.5")
    return (candle.close - candle.low) / spread


def _baseline(candles: Sequence[NormalizedCandle], index: int, *, window: int) -> tuple[Decimal, Decimal]:
    if index < window:
        raise ValueError("insufficient baseline")
    prior = candles[index-window:index]
    avg_volume = sum((bar.volume for bar in prior), Decimal("0")) / Decimal(window)
    avg_spread = sum((bar.high - bar.low for bar in prior), Decimal("0")) / Decimal(window)
    if avg_volume <= 0 or avg_spread <= 0:
        raise ValueError("non-positive VSA baseline")
    return avg_volume, avg_spread


def detect_vsa_events(
    candles: Sequence[NormalizedCandle],
    *,
    baseline_window: int = 20,
    narrow_spread_max: Decimal = Decimal("0.8"),
    wide_spread_min: Decimal = Decimal("1.5"),
    low_volume_max: Decimal = Decimal("0.8"),
    high_volume_min: Decimal = Decimal("1.8"),
    stopping_volume_min: Decimal = Decimal("1.5"),
) -> tuple[VSAEvent, ...]:
    if baseline_window < 2:
        raise ValueError("baseline_window must be >= 2")
    if len(candles) <= baseline_window:
        return ()
    first = candles[0]
    validate_sequence(candles, provider_id=first.provider_id, symbol=first.symbol, interval=first.interval, require_closed=True, require_contiguous=True)

    events: list[VSAEvent] = []
    for index in range(baseline_window, len(candles)):
        bar = candles[index]
        avg_volume, avg_spread = _baseline(candles, index, window=baseline_window)
        spread = bar.high - bar.low
        rel_volume = bar.volume / avg_volume
        rel_spread = spread / avg_spread
        close_loc = _close_location(bar)
        prior1, prior2 = candles[index-1], candles[index-2]
        lower_than_prior_two = bar.volume < prior1.volume and bar.volume < prior2.volume

        detected: list[tuple[str, str, tuple[str, ...]]] = []
        if bar.close < bar.open and rel_spread <= narrow_spread_max and rel_volume <= low_volume_max and lower_than_prior_two and close_loc >= Decimal("0.5"):
            detected.append(("NS", "LONG", ("DOWN_BAR", "NARROW_SPREAD", "LOW_VOLUME")))
        if bar.close > bar.open and rel_spread <= narrow_spread_max and rel_volume <= low_volume_max and lower_than_prior_two and close_loc <= Decimal("0.5"):
            detected.append(("ND", "SHORT", ("UP_BAR", "NARROW_SPREAD", "LOW_VOLUME")))
        if bar.low < min(prior1.low, prior2.low) and close_loc >= Decimal("0.6") and rel_spread <= Decimal("1.0") and rel_volume <= Decimal("1.0"):
            detected.append(("T", "LONG", ("LOW_PROBE", "CLOSE_OFF_LOW", "CONTROLLED_VOLUME")))
        if bar.high > max(prior1.high, prior2.high) and close_loc <= Decimal("0.35") and rel_spread >= Decimal("1.2") and rel_volume >= Decimal("1.2"):
            detected.append(("UT", "SHORT", ("HIGH_PROBE", "CLOSE_OFF_HIGH", "EXPANSION")))
        if bar.close >= bar.open and rel_spread >= wide_spread_min and rel_volume >= high_volume_min and close_loc <= Decimal("0.75"):
            detected.append(("BC", "SHORT", ("WIDE_UP_BAR", "CLIMACTIC_VOLUME", "CLOSE_OFF_HIGH")))
        if bar.close <= bar.open and rel_spread >= wide_spread_min and rel_volume >= high_volume_min and close_loc >= Decimal("0.25"):
            detected.append(("SC", "LONG", ("WIDE_DOWN_BAR", "CLIMACTIC_VOLUME", "CLOSE_OFF_LOW")))
        if bar.close <= bar.open and rel_volume >= stopping_volume_min and rel_spread <= Decimal("1.0") and close_loc >= Decimal("0.5"):
            detected.append(("SV", "LONG", ("HIGH_VOLUME", "NARROW_OR_NORMAL_SPREAD", "CLOSE_OFF_LOW")))

        for event_type, direction, reasons in detected:
            events.append(VSAEvent(
                event_type=event_type,
                provider_id=bar.provider_id,
                symbol=bar.symbol,
                timeframe=bar.interval,
                bar_index=index,
                bar_time=bar.close_time,
                direction=direction,
                relative_volume=rel_volume,
                relative_spread=rel_spread,
                close_location=close_loc,
                raw_quality="STRONG" if len(reasons) >= 3 else "BASE",
                reasons=reasons,
            ))
    return tuple(events)


def _matching_level(
    event: VSAEvent,
    bar: NormalizedCandle,
    levels: MTFLevelMap,
    *,
    atr14: Decimal,
    max_level_distance_atr_fraction: Decimal,
) -> PriceLevel | None:
    max_distance = atr14 * max_level_distance_atr_fraction
    side = "SUPPORT" if event.direction == "LONG" else "RESISTANCE"
    candidates = [level for level in levels.active() if level.side == side]
    if not candidates:
        return None

    def distance(level: PriceLevel) -> Decimal:
        if bar.high >= level.lower and bar.low <= level.upper:
            return Decimal("0")
        if bar.low > level.upper:
            return bar.low - level.upper
        return level.lower - bar.high

    nearest = min(candidates, key=distance)
    return nearest if distance(nearest) <= max_distance else None


def validate_vsa_context(
    events: Sequence[VSAEvent],
    candles: Sequence[NormalizedCandle],
    *,
    levels: MTFLevelMap,
    mtf_regime: MTFRegimeSnapshot,
    traps: Sequence[TrapEvent] = (),
    atr14: Decimal,
    max_level_distance_atr_fraction: Decimal = Decimal("0.25"),
    confirmation_bars: int = 2,
) -> tuple[VSAEvent, ...]:
    if atr14 <= 0:
        raise ValueError("ATR14 must be positive")
    if max_level_distance_atr_fraction < 0:
        raise ValueError("level-distance fraction cannot be negative")
    if confirmation_bars <= 0:
        raise ValueError("confirmation_bars must be positive")
    if not candles:
        return ()
    first = candles[0]
    validate_sequence(candles, provider_id=first.provider_id, symbol=first.symbol, interval=first.interval, require_closed=True, require_contiguous=True)

    validated: list[VSAEvent] = []
    for event in events:
        if event.bar_index >= len(candles):
            raise ValueError("VSA event index outside candle sequence")
        bar = candles[event.bar_index]
        expected_regime = "BULLISH" if event.direction == "LONG" else "BEARISH"
        level = _matching_level(event, bar, levels, atr14=atr14, max_level_distance_atr_fraction=max_level_distance_atr_fraction)
        trap_match = any(
            trap.confirmed
            and trap.direction == event.direction
            and trap.provider_id == event.provider_id
            and trap.symbol == event.symbol
            and level is not None
            and trap.level_id == level.level_id
            and trap.confirmation_time is not None
            and trap.confirmation_time <= event.bar_time
            for trap in traps
        )

        if mtf_regime.regime != expected_regime:
            validated.append(replace(event, context_status="IGNORED", invalidation_reason="HTF_CONTEXT_MISMATCH"))
            continue
        if level is None:
            validated.append(replace(event, context_status="IGNORED", invalidation_reason="NO_CONFIRMED_LEVEL_LOCATION"))
            continue

        confirmation_index: int | None = None
        end = min(len(candles), event.bar_index + 1 + confirmation_bars)
        for index in range(event.bar_index + 1, end):
            candidate = candles[index]
            confirmed = candidate.close > bar.high if event.direction == "LONG" else candidate.close < bar.low
            if confirmed:
                confirmation_index = index
                break

        if confirmation_index is None:
            validated.append(replace(
                event,
                context_status="VALID_CONTEXT",
                confirmed=False,
                reference_level_id=level.level_id,
                trap_confirmed=trap_match,
                invalidation_reason="AWAITING_CONFIRMATION",
            ))
            continue

        validated.append(replace(
            event,
            context_status="CONFIRMED",
            confirmed=True,
            reference_level_id=level.level_id,
            trap_confirmed=trap_match,
            invalidation_reason=None,
        ))
    return tuple(validated)
