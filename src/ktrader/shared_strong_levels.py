"""Shared causal D1/W1 level registry for research strategies S1-S5.

The upstream automatic strong-level selector is the only authority for level
qualification. This module does not invent a second admission algorithm.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Mapping

STRATEGIES = frozenset({"S1", "S2A", "S2B", "S3", "S4", "S5A", "S5B"})


@dataclass(frozen=True)
class StrongLevel:
    price: Decimal
    timeframe: str
    side: str
    known_at_ms: int
    source_id: str
    strength: str

    def __post_init__(self):
        if self.timeframe not in ("D1", "W1"):
            raise ValueError("D1/W1 required")
        if self.side not in ("SUPPORT", "RESISTANCE"):
            raise ValueError("invalid side")
        if not self.price.is_finite() or self.price <= 0:
            raise ValueError("invalid level price")
        if type(self.known_at_ms) is not int or self.known_at_ms < 0:
            raise ValueError("invalid causal availability")
        if not self.source_id or not self.strength:
            raise ValueError("missing selection evidence")


def shared_levels(
    selected: Iterable[Mapping],
    *,
    strategy: str,
    as_of_ms: int,
) -> tuple[StrongLevel, ...]:
    """Distribute ONE automatically selected strong-level set to every model.

    `selected` must be the output of the approved strong-level engine,
    not unqualified archetype candidates or reviewer placeholders.
    """
    if strategy not in STRATEGIES:
        raise ValueError("unsupported strategy")
    if type(as_of_ms) is not int or as_of_ms < 0:
        raise ValueError("invalid cutoff")
    output = {}
    for item in selected:
        if item.get("selection_status") != "STRONG_CONFIRMED":
            continue
        level = StrongLevel(
            price=Decimal(str(item["price"])),
            timeframe=item["timeframe"],
            side=item["side"],
            known_at_ms=item["known_at_ms"],
            source_id=item["source_id"],
            strength=item["strength"],
        )
        if level.known_at_ms > as_of_ms:
            continue
        key = (level.timeframe, level.price, level.side)
        previous = output.get(key)
        if previous is None or (level.known_at_ms, level.source_id) < (
            previous.known_at_ms, previous.source_id
        ):
            output[key] = level
    return tuple(sorted(
        output.values(),
        key=lambda x: (x.known_at_ms, x.timeframe, x.price, x.side),
    ))
