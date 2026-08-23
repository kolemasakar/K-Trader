from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from collections.abc import Sequence
from typing import Any

from ktrader.evidence.trap import detect_level_traps
from ktrader.market.validation import validate_sequence
from ktrader.models import NormalizedCandle
from ktrader.structure.levels import PriceLevel, update_level


@dataclass(frozen=True, slots=True)
class ReplayObservation:
    index: int
    timestamp: datetime
    state: str
    confirmed: bool | None = None


def validate_replay_series(candles: Sequence[NormalizedCandle]) -> None:
    if not candles:
        raise ValueError("replay candle sequence is empty")
    first = candles[0]
    validate_sequence(
        candles,
        provider_id=first.provider_id,
        symbol=first.symbol,
        interval=first.interval,
        require_closed=True,
        require_contiguous=True,
    )


def replay_level_lifecycle(
    level: PriceLevel,
    candles: Sequence[NormalizedCandle],
) -> tuple[ReplayObservation, ...]:
    validate_replay_series(candles)
    if candles[0].provider_id != level.provider_id or candles[0].symbol != level.symbol:
        raise ValueError("replay level/candle identity mismatch")
    current = level
    observations: list[ReplayObservation] = []
    for index, candle in enumerate(candles):
        current = update_level(current, candle)
        observations.append(
            ReplayObservation(index, candle.close_time, current.status, current.status in {"CONFIRMED", "MIRROR"})
        )
    return tuple(observations)


def replay_trap_states(
    candles: Sequence[NormalizedCandle],
    level: PriceLevel,
    *,
    atr14: Decimal,
    min_break_atr_fraction: Decimal = Decimal("0.05"),
    max_return_bars: int = 3,
    max_confirmation_bars: int = 2,
) -> tuple[ReplayObservation, ...]:
    validate_replay_series(candles)
    observations: list[ReplayObservation] = []
    for end in range(1, len(candles) + 1):
        prefix = candles[:end]
        events = detect_level_traps(
            prefix,
            level,
            atr14=atr14,
            min_break_atr_fraction=min_break_atr_fraction,
            max_return_bars=max_return_bars,
            max_confirmation_bars=max_confirmation_bars,
        )
        event = events[-1] if events else None
        observations.append(
            ReplayObservation(
                end - 1,
                prefix[-1].close_time,
                event.status if event else "NONE",
                event.confirmed if event else False,
            )
        )
    return tuple(observations)


def canonical_digest(value: Any) -> str:
    normalized = _normalize(value)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(payload.encode("ascii")).hexdigest()


def _normalize(value: Any) -> Any:
    if is_dataclass(value):
        return _normalize(asdict(value))
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_normalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
