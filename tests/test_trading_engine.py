from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest

from ktrader.engine import RiskContext, SetupCandidate, SetupGeometry, build_daily_range_context, build_setup_geometry, calculate_position_risk, choose_best_decision, discover_setup_candidates, evaluate_candidate
from ktrader.engine.scoring import score_setup
from ktrader.evidence.trap import TrapEvent
from ktrader.evidence.vsa import VSAEvent
from ktrader.market.universe import UniverseCandidate
from ktrader.market.validation import FreshnessResult
from ktrader.models import NormalizedCandle, NormalizedInstrument, NormalizedTicker
from ktrader.structure.levels import MTFLevelMap, PriceLevel
from ktrader.structure.sessions import SessionContext
from ktrader.structure.snapshot import MarketStructureSnapshot

UTC = timezone.utc
BASE = datetime(2026, 8, 23, 0, 0, tzinfo=UTC)


def candle(i, o, h, l, c):
    ot = BASE + timedelta(minutes=5 * i)
    return NormalizedCandle("test", "XUSDT", "5m", ot, ot + timedelta(minutes=5) - timedelta(milliseconds=1), Decimal(o), Decimal(h), Decimal(l), Decimal(c), Decimal("100"), closed=True)


def price_level(level_id, lower, upper, side, strength="STRONG", touches=3):
    return PriceLevel(level_id, "test", "XUSDT", "1h", Decimal(lower), Decimal(upper), side, "CONFIRMED", ("HISTORICAL",), touches, strength, BASE, BASE)


def regime(direction="LONG"):
    return SimpleNamespace(
        regime=direction,
        by_interval={tf: SimpleNamespace(regime=direction) for tf in ("1d", "4h", "1h")},
        strength_by_interval={tf: SimpleNamespace(evidence_count=3) for tf in ("1d", "4h", "1h")},
    )


@pytest.fixture
def market():
    candles = [candle(i, str(100+i/10), str(101+i/10), str(99+i/10), str(100.5+i/10)) for i in range(30)]
    candles[10] = candle(10, "100", "101", "99", "100")
    candles[11] = candle(11, "100", "102", "100", "101.5")
    candles[12] = candle(12, "101.5", "103", "101", "102.5")
    support = price_level("L1", "98", "99", "SUPPORT")
    resistance = price_level("R2", "120", "121", "RESISTANCE")
    levels = MTFLevelMap((support, resistance))
    trap = TrapEvent("test", "XUSDT", "5m", "LONG", "L1", "SUPPORT", Decimal("98"), Decimal("99"), candles[8].close_time, Decimal("97.5"), Decimal("97"), Decimal("1"), candles[9].close_time, candles[11].close_time, "CONFIRMED", True)
    vsa = VSAEvent("NS", "test", "XUSDT", "5m", 10, candles[10].close_time, "LONG", Decimal("0.7"), Decimal("0.7"), Decimal("0.6"), "STRONG", "CONFIRMED", True, "L1")
    session = SessionContext(candles[-1].close_time, ("LONDON", "NEW_YORK"), True, candles[-1].close_time)
    structure = MarketStructureSnapshot(candles[-1].close_time, regime(), session, levels)
    instrument = NormalizedInstrument("test", "XUSDT", "X", "USDT", "PERPETUAL", "PERPETUAL", "TRADING", Decimal("0.1"), Decimal("0.1"), "XUSDT")
    ticker = NormalizedTicker("test", "XUSDT", candles[-1].close_time, Decimal("103"), quote_volume_24h=Decimal("1000000"))
    universe = UniverseCandidate(instrument, ticker, Decimal("1000000"))
    freshness = FreshnessResult("5m", candles[-1].close_time, 5.0, 600.0, False)
    day = build_daily_range_context(candles)
    candidate = discover_setup_candidates(levels, traps=(trap,), vsa_events=(vsa,))[0]
    geometry = build_setup_geometry(candidate, candles, levels=levels, atr14=Decimal("4"), atr5d=Decimal("20"), day_range=day, price_tick=Decimal("0.1"))
    return SimpleNamespace(candles=candles, support=support, resistance=resistance, levels=levels, trap=trap, vsa=vsa, session=session, structure=structure, instrument=instrument, universe=universe, freshness=freshness, day=day, candidate=candidate, geometry=geometry)


def test_daily_range_starts_at_midnight(market):
    assert market.day.open_time == BASE and market.day.observed_low == Decimal("99")


def test_daily_range_rejects_partial_day(market):
    with pytest.raises(ValueError, match="00:00 UTC"):
        build_daily_range_context(market.candles[1:])


def test_discovers_trap_vsa_setup(market):
    assert market.candidate.setup_type == "TRAP_VSA_CONFIRMATION"


def test_discovers_vsa_only_setup(market):
    assert discover_setup_candidates(market.levels, traps=(), vsa_events=(market.vsa,))[0].setup_type == "VSA_LEVEL_CONFIRMATION"


def test_discovers_trap_only_setup(market):
    assert discover_setup_candidates(market.levels, traps=(market.trap,), vsa_events=())[0].setup_type == "TRAP_LEVEL_CONFIRMATION"


def test_geometry_uses_structural_target_and_rr(market):
    assert market.geometry.target_level_id == "R2" and market.geometry.rr >= 3 and market.geometry.entry > market.candles[11].high and market.geometry.stop < market.trap.sweep_extreme


def test_geometry_rejects_missing_structural_target(market):
    with pytest.raises(ValueError, match="no confirmed structural target"):
        build_setup_geometry(market.candidate, market.candles, levels=MTFLevelMap((market.support,)), atr14=Decimal("4"), atr5d=Decimal("20"), day_range=market.day, price_tick=Decimal("0.1"))


def test_atr_used_origin_is_directional_utc_day_excursion(market):
    expected = (market.geometry.entry - market.day.observed_low) / Decimal("20") * 100
    assert market.geometry.atr_used_pct == expected


def test_full_confluence_scores_a_plus(market):
    result = score_setup(market.candidate, market.geometry, regime=market.structure.regime, session=market.session, liquidity_rank=1, universe_size=10, liquidity_score=Decimal("1000000"), freshness_stale=False)
    assert result.grade == "A+" and result.raw_score >= 90 and not result.hard_rejects


def test_stale_data_hard_reject_caps_grade(market):
    result = score_setup(market.candidate, market.geometry, regime=market.structure.regime, session=market.session, liquidity_rank=1, universe_size=10, liquidity_score=Decimal("1"), freshness_stale=True)
    assert result.grade == "C" and result.setup_score <= 69 and "STALE_DATA" in result.hard_rejects


def test_primary_level_must_be_strong(market):
    moderate = price_level("L2", "98", "99", "SUPPORT", "MODERATE", 2)
    candidate = SetupCandidate("LONG", "TRAP_LEVEL_CONFIRMATION", moderate, trap=market.trap)
    result = score_setup(candidate, market.geometry, regime=market.structure.regime, session=market.session, liquidity_rank=1, universe_size=10, liquidity_score=Decimal("1"), freshness_stale=False)
    assert "PRIMARY_LEVEL_NOT_STRONG" in result.hard_rejects


def test_evidence_identity_mismatch_is_hard_reject(market):
    bad_vsa = VSAEvent("NS", "test", "XUSDT", "5m", 10, market.candles[10].close_time, "SHORT", Decimal("0.7"), Decimal("0.7"), Decimal("0.6"), "STRONG", "CONFIRMED", True, "L1")
    candidate = SetupCandidate("LONG", "TRAP_VSA_CONFIRMATION", market.support, trap=market.trap, vsa=bad_vsa)
    result = score_setup(candidate, market.geometry, regime=market.structure.regime, session=market.session, liquidity_rank=1, universe_size=10, liquidity_score=Decimal("1"), freshness_stale=False)
    assert "VSA_EVIDENCE_MISMATCH" in result.hard_rejects


def test_atr_used_over_80_is_hard_reject(market):
    late = SetupGeometry(market.geometry.confirmation_time, market.geometry.entry, market.geometry.luft, market.geometry.stop, market.geometry.target, market.geometry.target_level_id, market.geometry.rr, Decimal("81"), "LATE_REJECT")
    result = score_setup(market.candidate, late, regime=market.structure.regime, session=market.session, liquidity_rank=1, universe_size=10, liquidity_score=Decimal("1"), freshness_stale=False)
    assert "ATR_USED_OVER_80" in result.hard_rejects


def test_rr_below_three_is_hard_reject(market):
    low_rr = SetupGeometry(market.geometry.confirmation_time, market.geometry.entry, market.geometry.luft, market.geometry.stop, market.geometry.target, market.geometry.target_level_id, Decimal("2.9"), Decimal("20"), "STRONG")
    result = score_setup(market.candidate, low_rr, regime=market.structure.regime, session=market.session, liquidity_rank=1, universe_size=10, liquidity_score=Decimal("1"), freshness_stale=False)
    assert "RR_BELOW_3" in result.hard_rejects


def test_position_size_requires_explicit_risk_context(market):
    assert calculate_position_risk(market.geometry, None).position_size is None
    result = calculate_position_risk(market.geometry, RiskContext(Decimal("1000"), Decimal("1"), Decimal("1"), Decimal("0.1")))
    assert result.risk_amount == Decimal("10") and result.position_size > 0


def test_evaluate_candidate_emits_long_only_for_a_or_a_plus(market):
    decision = evaluate_candidate(market.candidate, instrument=market.instrument, universe_candidate=market.universe, liquidity_rank=1, universe_size=10, structure=market.structure, setup_candles=market.candles, day_range=market.day, freshness=market.freshness, atr14=Decimal("4"), atr5d=Decimal("20"), generated_at=market.candles[-1].close_time)
    assert decision.side == "LONG" and decision.grade in {"A+", "A"} and decision.entry is not None and not decision.reason_codes


def test_choose_best_prefers_tradable_over_rejected(market):
    good = evaluate_candidate(market.candidate, instrument=market.instrument, universe_candidate=market.universe, liquidity_rank=1, universe_size=10, structure=market.structure, setup_candles=market.candles, day_range=market.day, freshness=market.freshness, atr14=Decimal("4"), atr5d=Decimal("20"), generated_at=market.candles[-1].close_time)
    stale = FreshnessResult("5m", market.candles[-1].close_time, 1000.0, 600.0, True)
    rejected = evaluate_candidate(market.candidate, instrument=market.instrument, universe_candidate=market.universe, liquidity_rank=1, universe_size=10, structure=market.structure, setup_candles=market.candles, day_range=market.day, freshness=stale, atr14=Decimal("4"), atr5d=Decimal("20"), generated_at=market.candles[-1].close_time)
    assert choose_best_decision((rejected, good)) == good
