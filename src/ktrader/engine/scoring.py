from __future__ import annotations

from decimal import Decimal

from ktrader.engine.models import ScoreBreakdown, SetupCandidate, SetupGeometry
from ktrader.structure.regime import MTFRegimeSnapshot
from ktrader.structure.sessions import SessionContext


WEIGHTS = {
    "market_regime": 20,
    "liquidity": 10,
    "session": 5,
    "trap": 15,
    "mtf_level": 15,
    "strength": 10,
    "vsa": 15,
    "atr": 5,
    "rr": 5,
}

SIDE_TO_REGIME = {
    "LONG": "BULLISH",
    "SHORT": "BEARISH",
}


def _regime_matches_side(regime_value: str, side: str) -> bool:
    """Match canonical market-regime vocabulary to trading-side vocabulary.

    Production structure classification emits BULLISH/BEARISH while setup
    evidence emits LONG/SHORT. Accept the legacy side-shaped value as well so
    existing test doubles and callers remain compatible during the contract
    correction.
    """
    expected = SIDE_TO_REGIME.get(side)
    if expected is None:
        return regime_value == side
    return regime_value in {expected, side}


def context_strength(regime: MTFRegimeSnapshot, direction: str) -> str:
    by_tf = regime.by_interval
    strengths = regime.strength_by_interval

    def count(interval: str) -> int:
        return strengths[interval].evidence_count if interval in strengths else 0

    if (
        "1d" in by_tf and "4h" in by_tf
        and _regime_matches_side(by_tf["1d"].regime, direction)
        and _regime_matches_side(by_tf["4h"].regime, direction)
    ):
        evidence = min(count("1d"), count("4h"))
    elif (
        "4h" in by_tf and "1h" in by_tf
        and _regime_matches_side(by_tf["4h"].regime, direction)
        and _regime_matches_side(by_tf["1h"].regime, direction)
    ):
        evidence = min(count("4h"), count("1h"))
    else:
        evidence = 0
    return "STRONG" if evidence >= 3 else "MODERATE" if evidence == 2 else "WEAK"


def grade_for_score(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    return "C"


def score_setup(
    candidate: SetupCandidate,
    geometry: SetupGeometry | None,
    *,
    regime: MTFRegimeSnapshot,
    session: SessionContext,
    liquidity_rank: int,
    universe_size: int,
    liquidity_score: Decimal,
    freshness_stale: bool,
    geometry_error: str | None = None,
) -> ScoreBreakdown:
    hard: list[str] = []
    direction = candidate.direction

    if freshness_stale:
        hard.append("STALE_DATA")
    if liquidity_score <= 0 or liquidity_rank <= 0 or universe_size <= 0 or liquidity_rank > universe_size:
        hard.append("INVALID_LIQUIDITY_CONTEXT")
    if not _regime_matches_side(regime.regime, direction):
        hard.append("HTF_CONTEXT_MISMATCH")
    if candidate.primary_level.status not in {"CONFIRMED", "MIRROR"}:
        hard.append("PRIMARY_LEVEL_NOT_CONFIRMED")
    if candidate.primary_level.strength != "STRONG":
        hard.append("PRIMARY_LEVEL_NOT_STRONG")
    if candidate.trap is None and candidate.vsa is None:
        hard.append("NO_CONFIRMED_SETUP_EVIDENCE")

    expected_setup_type = (
        "TRAP_VSA_CONFIRMATION"
        if candidate.trap is not None and candidate.vsa is not None
        else "VSA_LEVEL_CONFIRMATION"
        if candidate.vsa is not None
        else "TRAP_LEVEL_CONFIRMATION"
    )
    if candidate.setup_type != expected_setup_type:
        hard.append("SETUP_TYPE_MISMATCH")

    if candidate.trap is not None:
        if not candidate.trap.confirmed or candidate.trap.status != "CONFIRMED":
            hard.append("TRAP_NOT_CONFIRMED")
        if (
            candidate.trap.direction != direction
            or candidate.trap.level_id != candidate.primary_level.level_id
            or candidate.trap.provider_id != candidate.primary_level.provider_id
            or candidate.trap.symbol != candidate.primary_level.symbol
        ):
            hard.append("TRAP_EVIDENCE_MISMATCH")

    if candidate.vsa is not None:
        if not candidate.vsa.confirmed or candidate.vsa.context_status != "CONFIRMED":
            hard.append("VSA_NOT_CONFIRMED")
        if (
            candidate.vsa.direction != direction
            or candidate.vsa.reference_level_id != candidate.primary_level.level_id
            or candidate.vsa.provider_id != candidate.primary_level.provider_id
            or candidate.vsa.symbol != candidate.primary_level.symbol
        ):
            hard.append("VSA_EVIDENCE_MISMATCH")
    if geometry is None:
        hard.append(geometry_error or "GEOMETRY_UNAVAILABLE")
    elif geometry.atr_used_pct > Decimal("80"):
        hard.append("ATR_USED_OVER_80")
    elif geometry.rr < Decimal("3"):
        hard.append("RR_BELOW_3")

    components: dict[str, int] = {}
    components["market_regime"] = WEIGHTS["market_regime"] if _regime_matches_side(regime.regime, direction) else 0

    if liquidity_rank > 0 and universe_size > 0 and liquidity_rank <= universe_size:
        fraction = Decimal(liquidity_rank) / Decimal(universe_size)
        components["liquidity"] = 10 if fraction <= Decimal("0.2") else 7 if fraction <= Decimal("0.5") else 4
    else:
        components["liquidity"] = 0

    components["session"] = 5 if session.overlap else 3 if session.active_sessions else 0
    components["trap"] = 15 if candidate.trap is not None and candidate.trap.confirmed else 0
    components["mtf_level"] = 15 if candidate.primary_level.strength == "STRONG" else 10 if candidate.primary_level.strength == "MODERATE" else 4

    strength = context_strength(regime, direction)
    components["strength"] = 10 if strength == "STRONG" else 6 if strength == "MODERATE" else 2
    components["vsa"] = 15 if candidate.vsa is not None and candidate.vsa.confirmed else 0

    if geometry is None:
        components["atr"] = 0
        components["rr"] = 0
    else:
        components["atr"] = 5 if geometry.atr_used_pct < Decimal("40") else 3 if geometry.atr_used_pct <= Decimal("80") else 0
        components["rr"] = 5 if geometry.rr >= Decimal("4") else 3 if geometry.rr >= Decimal("3") else 0

    raw_score = sum(components.values())
    setup_score = min(raw_score, 69) if hard else raw_score
    grade = "C" if hard else grade_for_score(setup_score)
    return ScoreBreakdown(
        components=components,
        raw_score=raw_score,
        setup_score=setup_score,
        grade=grade,
        hard_rejects=tuple(dict.fromkeys(hard)),
    )
