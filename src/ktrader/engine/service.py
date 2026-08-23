from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_FLOOR
from collections.abc import Sequence

from ktrader.evidence.trap import TrapEvent
from ktrader.evidence.vsa import VSAEvent
from ktrader.market.universe import UniverseCandidate
from ktrader.market.validation import FreshnessResult
from ktrader.models import NormalizedCandle, NormalizedInstrument
from ktrader.structure.levels import MTFLevelMap, PriceLevel
from ktrader.structure.snapshot import MarketStructureSnapshot
from ktrader.engine.geometry import build_setup_geometry
from ktrader.engine.models import (
    DailyRangeContext,
    PositionRisk,
    RiskContext,
    SetupCandidate,
    SetupGeometry,
    TradingDecision,
)
from ktrader.engine.scoring import context_strength, score_setup


def discover_setup_candidates(
    levels: MTFLevelMap,
    *,
    traps: Sequence[TrapEvent],
    vsa_events: Sequence[VSAEvent],
) -> tuple[SetupCandidate, ...]:
    active_by_id = {level.level_id: level for level in levels.active()}
    traps_by_key = {
        (event.direction, event.level_id): event
        for event in traps
        if event.confirmed and event.level_id in active_by_id
    }
    vsa_by_key = {
        (event.direction, event.reference_level_id): event
        for event in vsa_events
        if event.confirmed
        and event.reference_level_id is not None
        and event.reference_level_id in active_by_id
    }

    keys = set(traps_by_key) | set(vsa_by_key)
    candidates: list[SetupCandidate] = []
    for direction, level_id in keys:
        trap = traps_by_key.get((direction, level_id))
        vsa = vsa_by_key.get((direction, level_id))
        if trap is not None and vsa is not None:
            setup_type = "TRAP_VSA_CONFIRMATION"
        elif vsa is not None:
            setup_type = "VSA_LEVEL_CONFIRMATION"
        else:
            setup_type = "TRAP_LEVEL_CONFIRMATION"
        candidates.append(
            SetupCandidate(
                direction=direction,
                setup_type=setup_type,
                primary_level=active_by_id[level_id],
                trap=trap,
                vsa=vsa,
            )
        )
    candidates.sort(
        key=lambda item: max(
            item.trap.confirmation_time if item.trap and item.trap.confirmation_time else datetime.min.replace(tzinfo=timezone.utc),
            item.vsa.bar_time if item.vsa else datetime.min.replace(tzinfo=timezone.utc),
        ),
        reverse=True,
    )
    return tuple(candidates)


def calculate_position_risk(
    geometry: SetupGeometry,
    risk_context: RiskContext | None,
) -> PositionRisk:
    if risk_context is None:
        return PositionRisk(None, None, None)
    if (
        risk_context.balance <= 0
        or risk_context.risk_per_trade_pct <= 0
        or risk_context.quantity_value_per_price_unit <= 0
        or risk_context.quantity_step <= 0
    ):
        raise ValueError("risk context values must be positive")
    risk_amount = risk_context.balance * risk_context.risk_per_trade_pct / Decimal("100")
    per_quantity_risk = abs(geometry.entry - geometry.stop) * risk_context.quantity_value_per_price_unit
    if per_quantity_risk <= 0:
        raise ValueError("per-quantity risk must be positive")
    raw_quantity = risk_amount / per_quantity_risk
    steps = (raw_quantity / risk_context.quantity_step).to_integral_value(rounding=ROUND_FLOOR)
    quantity = steps * risk_context.quantity_step
    if quantity <= 0:
        return PositionRisk(Decimal("0"), risk_amount, risk_context.risk_per_trade_pct)
    return PositionRisk(quantity, risk_amount, risk_context.risk_per_trade_pct)


def evaluate_candidate(
    candidate: SetupCandidate,
    *,
    instrument: NormalizedInstrument,
    universe_candidate: UniverseCandidate,
    liquidity_rank: int,
    universe_size: int,
    structure: MarketStructureSnapshot,
    setup_candles: Sequence[NormalizedCandle],
    day_range: DailyRangeContext,
    freshness: FreshnessResult,
    atr14: Decimal,
    atr5d: Decimal,
    risk_context: RiskContext | None = None,
    generated_at: datetime | None = None,
    luft_atr_fraction: Decimal = Decimal("0.02"),
) -> TradingDecision:
    now = generated_at or datetime.now(timezone.utc)
    if instrument.provider_id != candidate.primary_level.provider_id or instrument.symbol != candidate.primary_level.symbol:
        raise ValueError("instrument/candidate identity mismatch")
    if universe_candidate.instrument.instrument_id != instrument.instrument_id:
        raise ValueError("universe candidate identity mismatch")

    geometry: SetupGeometry | None = None
    geometry_error: str | None = None
    if instrument.price_tick is None or instrument.price_tick <= 0:
        geometry_error = "MISSING_PRICE_TICK"
    else:
        try:
            geometry = build_setup_geometry(
                candidate,
                setup_candles,
                levels=structure.levels,
                atr14=atr14,
                atr5d=atr5d,
                day_range=day_range,
                price_tick=instrument.price_tick,
                luft_atr_fraction=luft_atr_fraction,
            )
        except ValueError as exc:
            message = str(exc)
            geometry_error = {
                "no confirmed structural target": "NO_STRUCTURAL_TARGET",
                "setup has no confirmed trigger bar": "MISSING_CONFIRMATION",
            }.get(message, "INVALID_GEOMETRY")

    score = score_setup(
        candidate,
        geometry,
        regime=structure.regime,
        session=structure.session,
        liquidity_rank=liquidity_rank,
        universe_size=universe_size,
        liquidity_score=universe_candidate.liquidity_score,
        freshness_stale=freshness.stale,
        geometry_error=geometry_error,
    )

    position = PositionRisk(None, None, None)
    reason_codes = list(score.hard_rejects)
    if geometry is not None:
        try:
            position = calculate_position_risk(geometry, risk_context)
            if risk_context is not None and position.position_size == 0:
                reason_codes.append("POSITION_SIZE_BELOW_STEP")
        except ValueError:
            reason_codes.append("INVALID_RISK_CONTEXT")

    eligible = not reason_codes and score.grade in {"A+", "A"}
    side = candidate.direction if eligible else "NO_TRADE"
    strength = context_strength(structure.regime, candidate.direction)
    provider_symbol = instrument.provider_symbol or instrument.symbol
    vsa_events = (candidate.vsa.event_type,) if candidate.vsa is not None else ()

    return TradingDecision(
        provider_id=instrument.provider_id,
        exchange=instrument.provider_id,
        canonical_symbol=instrument.symbol,
        provider_symbol=provider_symbol,
        market_type=instrument.market_type,
        side=side,
        grade=score.grade if not reason_codes else "C",
        setup_score=score.setup_score if not reason_codes else min(score.setup_score, 69),
        raw_score=score.raw_score,
        setup_type=candidate.setup_type,
        market_regime=structure.regime.regime,
        trend_context=structure.regime.regime,
        liquidity_rank=liquidity_rank,
        liquidity_score=universe_candidate.liquidity_score,
        sessions=structure.session.active_sessions,
        session_overlap=structure.session.overlap,
        strength=strength,
        primary_level_id=candidate.primary_level.level_id,
        primary_level_strength=candidate.primary_level.strength,
        trap_state=candidate.trap.status if candidate.trap is not None else None,
        vsa_events=vsa_events,
        entry=geometry.entry if geometry and side != "NO_TRADE" else None,
        luft=geometry.luft if geometry and side != "NO_TRADE" else None,
        stop=geometry.stop if geometry and side != "NO_TRADE" else None,
        target=geometry.target if geometry and side != "NO_TRADE" else None,
        rr=geometry.rr if geometry else None,
        atr5d=atr5d,
        atr_used_pct=geometry.atr_used_pct if geometry else None,
        atr_state=geometry.atr_state if geometry else None,
        position_size=position.position_size if side != "NO_TRADE" else None,
        risk_amount=position.risk_amount if side != "NO_TRADE" else None,
        risk_percent=position.risk_percent if side != "NO_TRADE" else None,
        reason_codes=tuple(dict.fromkeys(reason_codes or (("GRADE_BELOW_A",) if score.grade not in {"A+", "A"} else ()))),
        data_time=universe_candidate.ticker.timestamp,
        last_closed_bar=freshness.latest_close_time,
        data_age_seconds=freshness.age_seconds,
        freshness_status="STALE" if freshness.stale else "FRESH",
        generated_at=now,
    )


def choose_best_decision(decisions: Sequence[TradingDecision]) -> TradingDecision | None:
    if not decisions:
        return None
    return max(
        decisions,
        key=lambda item: (
            item.side != "NO_TRADE",
            item.setup_score,
            item.raw_score,
            item.rr or Decimal("0"),
        ),
    )
