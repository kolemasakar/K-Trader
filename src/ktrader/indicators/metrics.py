from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ATRUsedResult:
    move_distance: Decimal
    atr5d: Decimal
    pct: Decimal
    classification: str


def classify_atr_used(pct: Decimal) -> str:
    if pct < 0:
        raise ValueError("ATR used percent cannot be negative")
    if pct < Decimal("40"):
        return "STRONG"
    if pct <= Decimal("80"):
        return "ACCEPTABLE"
    return "LATE_REJECT"


def atr_used_pct(move_distance: Decimal, atr5d: Decimal) -> ATRUsedResult:
    if not atr5d.is_finite() or atr5d <= 0:
        raise ValueError("ATR5D must be finite and positive")
    if not move_distance.is_finite():
        raise ValueError("move_distance must be finite")
    distance = abs(move_distance)
    pct = distance / atr5d * Decimal("100")
    return ATRUsedResult(
        move_distance=distance,
        atr5d=atr5d,
        pct=pct,
        classification=classify_atr_used(pct),
    )
