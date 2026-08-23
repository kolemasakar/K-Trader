from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from collections.abc import Sequence

from ktrader.market.validation import validate_sequence
from ktrader.models import NormalizedCandle
from ktrader.structure.levels import PriceLevel


@dataclass(frozen=True, slots=True)
class TrapEvent:
    provider_id: str
    symbol: str
    timeframe: str
    direction: str
    level_id: str
    level_side: str
    reference_lower: Decimal
    reference_upper: Decimal
    break_time: datetime
    break_close: Decimal
    sweep_extreme: Decimal
    sweep_distance: Decimal
    return_time: datetime | None
    confirmation_time: datetime | None
    status: str
    confirmed: bool
    reason: str | None = None


def _validate_inputs(candles: Sequence[NormalizedCandle], level: PriceLevel, atr14: Decimal) -> None:
    if atr14 <= 0:
        raise ValueError("ATR14 must be positive")
    if level.status not in {"CONFIRMED", "MIRROR"}:
        raise ValueError("trap detection requires confirmed/mirror level")
    if level.side not in {"SUPPORT", "RESISTANCE"}:
        raise ValueError("trap detection requires support/resistance level")
    if not candles:
        raise ValueError("candle sequence is empty")
    validate_sequence(
        candles,
        provider_id=level.provider_id,
        symbol=level.symbol,
        interval=candles[0].interval,
        require_closed=True,
        require_contiguous=True,
    )


def detect_level_traps(
    candles: Sequence[NormalizedCandle],
    level: PriceLevel,
    *,
    atr14: Decimal,
    min_break_atr_fraction: Decimal = Decimal("0.05"),
    max_return_bars: int = 3,
    max_confirmation_bars: int = 2,
) -> tuple[TrapEvent, ...]:
    _validate_inputs(candles, level, atr14)
    if min_break_atr_fraction < 0:
        raise ValueError("min_break_atr_fraction cannot be negative")
    if max_return_bars <= 0 or max_confirmation_bars <= 0:
        raise ValueError("bar windows must be positive")

    min_break = atr14 * min_break_atr_fraction
    events: list[TrapEvent] = []
    i = 0
    while i < len(candles):
        candle = candles[i]
        if level.side == "SUPPORT":
            broke = candle.close < level.lower - min_break
            sweep_extreme = candle.low
            sweep_distance = max(level.lower - candle.low, Decimal("0"))
            direction = "LONG"
        else:
            broke = candle.close > level.upper + min_break
            sweep_extreme = candle.high
            sweep_distance = max(candle.high - level.upper, Decimal("0"))
            direction = "SHORT"

        if not broke:
            i += 1
            continue

        return_index: int | None = None
        return_end = min(len(candles), i + 1 + max_return_bars)
        for j in range(i + 1, return_end):
            candidate = candles[j]
            returned = candidate.close >= level.lower if level.side == "SUPPORT" else candidate.close <= level.upper
            if returned:
                return_index = j
                break

        if return_index is None:
            return_window_complete = len(candles) >= i + 1 + max_return_bars
            events.append(TrapEvent(
                provider_id=level.provider_id,
                symbol=level.symbol,
                timeframe=candles[0].interval,
                direction=direction,
                level_id=level.level_id,
                level_side=level.side,
                reference_lower=level.lower,
                reference_upper=level.upper,
                break_time=candle.close_time,
                break_close=candle.close,
                sweep_extreme=sweep_extreme,
                sweep_distance=sweep_distance,
                return_time=None,
                confirmation_time=None,
                status="EXPIRED" if return_window_complete else "BROKEN",
                confirmed=False,
                reason="NO_RETURN_THROUGH_LEVEL" if return_window_complete else "AWAITING_RETURN",
            ))
            i += 1
            continue

        returned_bar = candles[return_index]
        confirmation_index: int | None = None
        confirm_end = min(len(candles), return_index + 1 + max_confirmation_bars)
        for k in range(return_index + 1, confirm_end):
            candidate = candles[k]
            confirmed = candidate.close > returned_bar.high if direction == "LONG" else candidate.close < returned_bar.low
            if confirmed:
                confirmation_index = k
                break

        events.append(TrapEvent(
            provider_id=level.provider_id,
            symbol=level.symbol,
            timeframe=candles[0].interval,
            direction=direction,
            level_id=level.level_id,
            level_side=level.side,
            reference_lower=level.lower,
            reference_upper=level.upper,
            break_time=candle.close_time,
            break_close=candle.close,
            sweep_extreme=sweep_extreme,
            sweep_distance=sweep_distance,
            return_time=returned_bar.close_time,
            confirmation_time=candles[confirmation_index].close_time if confirmation_index is not None else None,
            status="CONFIRMED" if confirmation_index is not None else "RETURNED",
            confirmed=confirmation_index is not None,
            reason=None if confirmation_index is not None else "AWAITING_CONFIRMATION",
        ))
        i = return_index + 1
    return tuple(events)


def detect_traps(
    candles: Sequence[NormalizedCandle],
    levels: Sequence[PriceLevel],
    *,
    atr14: Decimal,
    min_break_atr_fraction: Decimal = Decimal("0.05"),
    max_return_bars: int = 3,
    max_confirmation_bars: int = 2,
) -> tuple[TrapEvent, ...]:
    events: list[TrapEvent] = []
    for level in levels:
        if level.status not in {"CONFIRMED", "MIRROR"} or level.side not in {"SUPPORT", "RESISTANCE"}:
            continue
        events.extend(detect_level_traps(
            candles,
            level,
            atr14=atr14,
            min_break_atr_fraction=min_break_atr_fraction,
            max_return_bars=max_return_bars,
            max_confirmation_bars=max_confirmation_bars,
        ))
    return tuple(sorted(events, key=lambda event: event.break_time))
