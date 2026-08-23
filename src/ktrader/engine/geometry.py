from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from collections.abc import Sequence

from ktrader.indicators.metrics import atr_used_pct
from ktrader.market.validation import validate_sequence
from ktrader.models import NormalizedCandle
from ktrader.structure.levels import MTFLevelMap, PriceLevel
from ktrader.evidence.vsa import VSAEvent
from ktrader.engine.models import DailyRangeContext, SetupCandidate, SetupGeometry


def _round_up(value: Decimal, tick: Decimal) -> Decimal:
    return (value / tick).to_integral_value(rounding=ROUND_CEILING) * tick


def _round_down(value: Decimal, tick: Decimal) -> Decimal:
    return (value / tick).to_integral_value(rounding=ROUND_FLOOR) * tick


def build_daily_range_context(
    candles_5m: Sequence[NormalizedCandle],
) -> DailyRangeContext:
    if not candles_5m:
        raise ValueError("5m day sequence is empty")
    first = candles_5m[0]
    if first.interval != "5m":
        raise ValueError("daily range context requires canonical 5m candles")
    validate_sequence(
        candles_5m,
        provider_id=first.provider_id,
        symbol=first.symbol,
        interval="5m",
        require_closed=True,
        require_contiguous=True,
    )
    day_start = first.open_time.astimezone(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if first.open_time != day_start:
        raise ValueError("daily range context must start at 00:00 UTC")
    if any(bar.open_time.date() != day_start.date() for bar in candles_5m):
        raise ValueError("daily range context cannot cross UTC day boundary")
    return DailyRangeContext(
        provider_id=first.provider_id,
        symbol=first.symbol,
        open_time=day_start,
        last_closed_bar=candles_5m[-1].close_time,
        observed_high=max(bar.high for bar in candles_5m),
        observed_low=min(bar.low for bar in candles_5m),
    )


def _vsa_confirmation_time(
    event: VSAEvent,
    candles: Sequence[NormalizedCandle],
    *,
    confirmation_bars: int = 2,
) -> datetime | None:
    if not event.confirmed or event.bar_index >= len(candles):
        return None
    source = candles[event.bar_index]
    end = min(len(candles), event.bar_index + 1 + confirmation_bars)
    for index in range(event.bar_index + 1, end):
        bar = candles[index]
        confirmed = bar.close > source.high if event.direction == "LONG" else bar.close < source.low
        if confirmed:
            return bar.close_time
    return None


def _confirmation_time(candidate: SetupCandidate, candles: Sequence[NormalizedCandle]) -> datetime:
    times: list[datetime] = []
    if candidate.trap is not None and candidate.trap.confirmed and candidate.trap.confirmation_time is not None:
        times.append(candidate.trap.confirmation_time)
    if candidate.vsa is not None:
        vsa_time = _vsa_confirmation_time(candidate.vsa, candles)
        if vsa_time is not None:
            times.append(vsa_time)
    if not times:
        raise ValueError("setup has no confirmed trigger bar")
    return max(times)


def _find_candle_at_close(
    candles: Sequence[NormalizedCandle],
    close_time: datetime,
) -> NormalizedCandle:
    for candle in candles:
        if candle.close_time == close_time:
            return candle
    raise ValueError("confirmation candle is outside setup sequence")


def _target_level(
    levels: MTFLevelMap,
    *,
    direction: str,
    entry: Decimal,
    primary_level_id: str,
) -> PriceLevel | None:
    active = [
        level for level in levels.active()
        if level.level_id != primary_level_id
    ]
    if direction == "LONG":
        candidates = [
            level for level in active
            if level.side == "RESISTANCE" and level.lower > entry
        ]
        return min(candidates, key=lambda level: level.lower, default=None)
    candidates = [
        level for level in active
        if level.side == "SUPPORT" and level.upper < entry
    ]
    return max(candidates, key=lambda level: level.upper, default=None)


def build_setup_geometry(
    candidate: SetupCandidate,
    candles: Sequence[NormalizedCandle],
    *,
    levels: MTFLevelMap,
    atr14: Decimal,
    atr5d: Decimal,
    day_range: DailyRangeContext,
    price_tick: Decimal,
    luft_atr_fraction: Decimal = Decimal("0.02"),
) -> SetupGeometry:
    if candidate.direction not in {"LONG", "SHORT"}:
        raise ValueError("unsupported setup direction")
    if atr14 <= 0 or atr5d <= 0 or price_tick <= 0:
        raise ValueError("ATR14, ATR5D and price_tick must be positive")
    if luft_atr_fraction < 0:
        raise ValueError("luft_atr_fraction cannot be negative")
    if day_range.provider_id != candidate.primary_level.provider_id or day_range.symbol != candidate.primary_level.symbol:
        raise ValueError("daily range identity mismatch")
    if not candles:
        raise ValueError("setup candle sequence is empty")
    first = candles[0]
    validate_sequence(
        candles,
        provider_id=candidate.primary_level.provider_id,
        symbol=candidate.primary_level.symbol,
        interval=first.interval,
        require_closed=True,
        require_contiguous=True,
    )

    confirmation_time = _confirmation_time(candidate, candles)
    confirmation_utc = confirmation_time.astimezone(timezone.utc)
    if confirmation_utc.date() != day_range.open_time.date():
        raise ValueError("setup confirmation is outside current UTC day")
    if confirmation_time > day_range.last_closed_bar:
        raise ValueError("daily range does not cover setup confirmation")
    confirmation_bar = _find_candle_at_close(candles, confirmation_time)
    luft = _round_up(max(price_tick, atr14 * luft_atr_fraction), price_tick)

    if candidate.direction == "LONG":
        entry = _round_up(confirmation_bar.high + luft, price_tick)
        stop_anchor = candidate.primary_level.lower
        if candidate.trap is not None:
            stop_anchor = min(stop_anchor, candidate.trap.sweep_extreme)
        stop = _round_down(stop_anchor - luft, price_tick)
    else:
        entry = _round_down(confirmation_bar.low - luft, price_tick)
        stop_anchor = candidate.primary_level.upper
        if candidate.trap is not None:
            stop_anchor = max(stop_anchor, candidate.trap.sweep_extreme)
        stop = _round_up(stop_anchor + luft, price_tick)

    target_level = _target_level(
        levels,
        direction=candidate.direction,
        entry=entry,
        primary_level_id=candidate.primary_level.level_id,
    )
    if target_level is None:
        raise ValueError("no confirmed structural target")
    if candidate.direction == "LONG":
        target = _round_down(target_level.lower - luft, price_tick)
        risk = entry - stop
        reward = target - entry
        move_distance = entry - day_range.observed_low
    else:
        target = _round_up(target_level.upper + luft, price_tick)
        risk = stop - entry
        reward = entry - target
        move_distance = day_range.observed_high - entry

    if risk <= 0 or reward <= 0:
        raise ValueError("invalid setup geometry")
    if move_distance < 0:
        raise ValueError("entry lies outside observed directional daily range")

    atr_used = atr_used_pct(move_distance, atr5d)
    return SetupGeometry(
        confirmation_time=confirmation_time,
        entry=entry,
        luft=luft,
        stop=stop,
        target=target,
        target_level_id=target_level.level_id,
        rr=reward / risk,
        atr_used_pct=atr_used.pct,
        atr_state=atr_used.classification,
    )
