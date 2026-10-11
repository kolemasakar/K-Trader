"""Gerchik-book-grounded engineering rating, 0..100; research only.

Weights/caps are an uncalibrated project model, not a formula from the book.
Upstream independent pattern reviews are required, never fabricated here.
No ATR, trade outcomes, probability, decay or live-order dependency.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

BASE = {"TREND_BREAK": 30, "MIRROR": 25, "HISTORICAL": 25, "LIMIT": 20,
        "CONSOLIDATION": 15, "PARANORMAL_BAR": 10, "GAP": 5}


@dataclass(frozen=True)
class SourceBar:
    bar_id: str
    symbol: str
    timeframe: str
    start: int
    end: int
    open: int
    high: int
    low: int
    close: int


@dataclass(frozen=True)
class Formation:
    level_id: str
    symbol: str
    price_ticks: int
    tick_size: str
    primary_type: str
    source_bar_id: str
    source_field: str
    formed_at: int
    known_at: int
    reviewer_id: str
    review_id: str
    review_at: int
    review_decision: str
    pattern_specification: str
    state: str


@dataclass(frozen=True)
class Proof:
    event_id: str
    kind: str
    source_bar_id: str
    side: str
    known_at: int
    reviewed_at: int
    reviewer_id: str
    review_decision: str
    reference_ticks: int | None = None
    reference_known_at: int | None = None
    related_bar_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Policy:
    provenance: str
    near_miss_ticks: int
    cross_tf_luft_ticks: int
    round_step_ticks: int | None
    round_offset_ticks: int
    round_policy_provenance: str


def rate(level: Formation, bars: Sequence[SourceBar], proofs: Sequence[Proof],
         policy: Policy, *, as_of: int) -> dict:
    """Rate reviewed formation + reviewed causal events available at cutoff.

    Review fields are trusted workflow declarations, not authentication.
    Physical D1/W1 overlap is allowed; exact duplicate records are rejected.
    Invalidations/role changes must be supplied by historical state upstream.
    """
    required = (level.level_id, level.symbol, level.source_bar_id, level.reviewer_id,
                level.review_id, level.pattern_specification, policy.provenance)
    if not all(isinstance(x, str) and x.strip() for x in required):
        raise ValueError("formation/parameter/review provenance required")
    if level.primary_type not in BASE or level.source_field not in ("high", "low"):
        raise ValueError("one valid primary type and High/Low source required")
    integers = (level.price_ticks, level.formed_at, level.known_at, level.review_at,
                policy.near_miss_ticks, policy.cross_tf_luft_ticks, policy.round_offset_ticks, as_of)
    if any(type(x) is not int for x in integers) or level.price_ticks <= 0:
        raise ValueError("integer price ticks and timestamps required")
    tick = Decimal(level.tick_size)
    if not tick.is_finite() or tick <= 0 or min(policy.near_miss_ticks, policy.cross_tf_luft_ticks) < 0:
        raise ValueError("invalid tick/tolerance")
    if policy.round_step_ticks is not None and (type(policy.round_step_ticks) is not int
                                               or policy.round_step_ticks <= 0
                                               or not isinstance(policy.round_policy_provenance, str)
                                               or not policy.round_policy_provenance.strip()):
        raise ValueError("round grid must be explicit and documented")
    sources = {}
    for bar in bars:
        if (bar.bar_id in sources or not bar.bar_id or bar.symbol != level.symbol
                or bar.timeframe not in ("1d", "1w")
                or any(type(x) is not int for x in (bar.start, bar.end, bar.open, bar.high, bar.low, bar.close))
                or bar.start >= bar.end or bar.low <= 0
                or not bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high):
            raise ValueError("invalid/duplicate source bar")
        sources[bar.bar_id] = bar
    if level.source_bar_id not in sources:
        raise ValueError("formation source missing")
    origin = sources[level.source_bar_id]
    if (getattr(origin, level.source_field) != level.price_ticks
            or not origin.end <= level.formed_at <= level.review_at <= level.known_at
            or level.review_decision != "APPROVED"):
        raise ValueError("source-price or causal formation review mismatch")
    base = {"model": "ktrader.gerchik_strength.v0.1", "level_id": level.level_id,
            "primary_type": level.primary_type, "as_of": as_of,
            "score": None, "grade": None, "probability": None,
            "calibration": "UNVALIDATED_ENGINEERING_WEIGHTS",
            "pattern_review": level.review_id, "policy_provenance": policy.provenance}
    if level.known_at > as_of or level.state != "CONFIRMED":
        return dict(base, status="NOT_RATEABLE", reason="LEVEL_NOT_CONFIRMED_AS_OF")
    seen_ids, seen_records = set(), set()
    contacts = {}
    new_extreme = cross_tf = False
    wick_fraction = Decimal(0)
    eligible_ids = []
    future_ids = []
    for proof in proofs:
        identity = (proof.source_bar_id, proof.kind)
        if not proof.event_id or proof.event_id in seen_ids or identity in seen_records:
            raise ValueError("duplicate evidence")
        seen_ids.add(proof.event_id)
        seen_records.add(identity)
        if proof.source_bar_id not in sources:
            raise ValueError("missing proof source")
        bar = sources[proof.source_bar_id]
        if (proof.side not in ("SUPPORT", "RESISTANCE")
                or proof.kind not in ("TOUCH", "NEAR_MISS", "FALSE_BREAKOUT", "NEW_EXTREME", "CROSS_TF")
                or not proof.reviewer_id or proof.review_decision != "APPROVED"
                or any(type(x) is not int for x in (proof.known_at, proof.reviewed_at))
                or not bar.end <= proof.known_at <= proof.reviewed_at):
            raise ValueError("invalid/unreviewed/noncausal evidence")
        if proof.reviewed_at > as_of:
            future_ids.append(proof.event_id)
            continue
        if proof.reviewed_at < level.known_at or bar.bar_id == level.source_bar_id:
            raise ValueError("formation cannot be counted as subsequent strengthening")
        if proof.kind != "CROSS_TF" and bar.start < level.known_at:
            raise ValueError("subsequent reactions must start after level availability")
        price = level.price_ticks
        boundary = bar.low if proof.side == "SUPPORT" else bar.high
        distance = boundary-price if proof.side == "SUPPORT" else price-boundary
        returned = bar.close > price if proof.side == "SUPPORT" else bar.close < price
        if proof.kind == "TOUCH" and not (distance == 0 and returned):
            raise ValueError("touch claim contradicted by OHLC")
        if proof.kind == "NEAR_MISS" and not (0 < distance <= policy.near_miss_ticks and returned):
            raise ValueError("near-miss claim contradicted by OHLC/tolerance")
        if proof.kind == "FALSE_BREAKOUT":
            if proof.related_bar_ids:
                if (len(proof.related_bar_ids) < 2
                        or len(set(proof.related_bar_ids)) != len(proof.related_bar_ids)
                        or proof.related_bar_ids[-1] != bar.bar_id
                        or any(key not in sources for key in proof.related_bar_ids)):
                    raise ValueError("complete unique false-break witness window required")
                window = [sources[key] for key in proof.related_bar_ids]
                starts_inside = window[0].open > price if proof.side == "SUPPORT" else window[0].open < price
                outside = all(x.close < price if proof.side == "SUPPORT" else x.close > price for x in window[:-1])
                if (not starts_inside or not outside or not returned
                        or any(x.timeframe != bar.timeframe or x.start < level.known_at
                               or x.end > proof.known_at for x in window)
                        or any(a.end != b.start for a, b in zip(window, window[1:]))):
                    raise ValueError("multibar false-break claim contradicted by causal OHLC")
            elif not (distance < 0 and returned):
                raise ValueError("single-bar false-break claim contradicted by OHLC")
        elif proof.related_bar_ids:
            raise ValueError("witness windows supported only for false breaks")
        if proof.kind in ("TOUCH", "NEAR_MISS", "FALSE_BREAKOUT"):
            previous = contacts.get(bar.bar_id)
            priority = {"NEAR_MISS": 1, "TOUCH": 2, "FALSE_BREAKOUT": 3}
            if previous is None or priority[proof.kind] > priority[previous]:
                contacts[bar.bar_id] = proof.kind
            length = bar.high-bar.low
            wick = min(bar.open, bar.close)-bar.low if proof.side == "SUPPORT" else bar.high-max(bar.open, bar.close)
            if length:
                wick_fraction = max(wick_fraction, Decimal(wick)/Decimal(length))
        elif proof.kind == "NEW_EXTREME":
            if (type(proof.reference_ticks) is not int or proof.reference_ticks <= 0
                    or type(proof.reference_known_at) is not int or proof.reference_known_at > bar.start
                    or not (bar.high > proof.reference_ticks if proof.side == "SUPPORT"
                            else bar.low < proof.reference_ticks)):
                raise ValueError("new swing-extreme reference must be causal and exceeded")
            new_extreme = True
        else:
            # Different TF/source record is enough; overlap must not reject it.
            if (bar.timeframe == origin.timeframe or bar.bar_id == origin.bar_id
                    or min(abs(bar.high-price), abs(bar.low-price)) > policy.cross_tf_luft_ticks):
                raise ValueError("cross-TF extremum/tolerance mismatch")
            cross_tf = True
        eligible_ids.append(proof.event_id)
    counts = {kind: sum(value == kind for value in contacts.values())
              for kind in ("TOUCH", "NEAR_MISS", "FALSE_BREAKOUT")}
    components = {"primary_type": Decimal(BASE[level.primary_type]),
                  "touches": Decimal(min(counts["TOUCH"], 6)*5),
                  "near_misses": Decimal(min(counts["NEAR_MISS"], 5)),
                  "false_breakouts": Decimal(min(counts["FALSE_BREAKOUT"], 3)*5),
                  "new_extreme": Decimal(10 if new_extreme else 0),
                  "rejection_wick": 5*wick_fraction,
                  "cross_tf": Decimal(5 if cross_tf else 0)}
    raw = sum(components.values(), Decimal(0))
    round_assessed = policy.round_step_ticks is not None
    is_round = round_assessed and (level.price_ticks-policy.round_offset_ticks) % policy.round_step_ticks == 0
    bonus = raw*Decimal("0.20") if is_round else Decimal(0)
    score = min(Decimal(100), raw+bonus).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    grade = "VERY_STRONG" if score >= 80 else "STRONG" if score >= 60 else "MODERATE" if score >= 40 else "WEAK"
    return dict(base, status="RATED_RESEARCH_ONLY", score=float(score), grade=grade,
                components={k: float(v) for k, v in components.items()},
                raw_score=float(raw), round_bonus=float(bonus), round_assessed=round_assessed,
                counts=counts, eligible_event_ids=sorted(eligible_ids),
                excluded_future_event_ids=sorted(future_ids))
