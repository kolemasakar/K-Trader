"""Research-only causal Gerchik level event ledger; not a pattern detector or trading signal.

A validated upstream detector must supply an independently qualified formation event.
This module only enforces identity, chronology and one immutable primary type.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

LEVEL_TYPES = frozenset({
    "TREND_BREAK", "HISTORICAL", "MIRROR", "LIMIT",
    "PARANORMAL_BAR", "CONSOLIDATION", "GAP",
})


@dataclass(frozen=True)
class Evidence:
    event_id: str
    kind: str
    observed_at: str
    source_bar_id: str


@dataclass
class Level:
    symbol: str
    timeframe: Literal["1d", "1w"]
    price_ticks: int
    tick_size: str
    primary_type: str
    formed_at: str
    formation_event_id: str
    evidence: list[Evidence] = field(default_factory=list)
    state: str = "CANDIDATE"

    @property
    def price(self) -> Decimal:
        return self.price_ticks * Decimal(self.tick_size)


def utc_time(value):
    if not isinstance(value, str):
        raise ValueError("Expected UTC ISO timestamp")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid ISO timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset().total_seconds() != 0:
        raise ValueError("Timestamp must use UTC")
    return dt.astimezone(timezone.utc)


class LevelLedger:
    """No archived pivot ingestion; callers must independently validate formations."""

    def __init__(self):
        self._levels = {}

    def record_formation(self, *, symbol, timeframe, price, tick_size,
                         primary_type, formed_at, formation_event_id,
                         source_field):
        if timeframe not in ("1d", "1w") or source_field not in ("high", "low"):
            raise ValueError("Only D1/W1 HIGH/LOW formation sources are allowed")
        if primary_type not in LEVEL_TYPES:
            raise ValueError("Unknown Gerchik primary type")
        if not symbol or not formed_at or not formation_event_id:
            raise ValueError("Missing provenance")
        utc_time(formed_at)
        tick = Decimal(str(tick_size))
        value = Decimal(str(price))
        if not tick.is_finite() or tick <= 0 or not value.is_finite() or value <= 0:
            raise ValueError("Invalid tick size or price")
        units = value / tick
        if units != units.to_integral_value():
            raise ValueError("Price must be an exact tick multiple")
        key = (symbol, timeframe, tick, int(units))
        if key in self._levels:
            raise ValueError("Level already exists: add evidence, not another primary type")
        level = Level(symbol, timeframe, int(units), str(tick), primary_type,
                      formed_at, formation_event_id,
                      state="CANDIDATE")
        self._levels[key] = level
        return level

    def add_evidence(self, level, evidence):
        if utc_time(evidence.observed_at) < utc_time(level.formed_at):
            raise ValueError("Cannot backdate strengthening evidence")
        if not evidence.event_id or not evidence.source_bar_id:
            raise ValueError("Missing evidence provenance")
        if evidence.event_id == level.formation_event_id:
            raise ValueError("Formation event cannot be double-counted")
        if any(item.event_id == evidence.event_id or
               (item.source_bar_id == evidence.source_bar_id and item.kind == evidence.kind)
               for item in level.evidence):
            raise ValueError("Duplicate evidence")
        level.evidence.append(evidence)

    def as_of(self, timestamp):
        cutoff = utc_time(timestamp)
        return [level for level in self._levels.values() if utc_time(level.formed_at) <= cutoff]
