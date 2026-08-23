from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.engine.models import TradingDecision
from ktrader.models import NormalizedCandle
from ktrader.outcomes import OutcomeRepository, decision_fingerprint, evaluate_signal_outcome

UTC = timezone.utc
BASE = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
LAST_CLOSED = BASE + timedelta(minutes=5) - timedelta(milliseconds=1)


def decision(*, side: str = "LONG") -> TradingDecision:
    tradable = side in {"LONG", "SHORT"}
    return TradingDecision(
        provider_id="p",
        exchange="p",
        canonical_symbol="XUSDT",
        provider_symbol="XUSDT",
        market_type="LINEAR_FUTURES",
        side=side,
        grade="A" if tradable else "C",
        setup_score=84 if tradable else 0,
        raw_score=84 if tradable else 0,
        setup_type="TRAP_VSA_CONFIRMATION" if tradable else "NO_SETUP",
        market_regime="BULLISH",
        trend_context="BULLISH",
        liquidity_rank=1,
        liquidity_score=Decimal("1000"),
        sessions=("LONDON",),
        session_overlap=False,
        strength="STRONG",
        primary_level_id="L1" if tradable else None,
        primary_level_strength="STRONG" if tradable else None,
        trap_state="CONFIRMED" if tradable else None,
        vsa_events=("NS",) if tradable else (),
        entry=Decimal("100") if tradable else None,
        luft=Decimal("0") if tradable else None,
        stop=Decimal("95") if tradable else None,
        target=Decimal("115") if tradable else None,
        rr=Decimal("3") if tradable else None,
        atr5d=Decimal("20"),
        atr_used_pct=Decimal("20") if tradable else None,
        atr_state="STRONG" if tradable else None,
        position_size=None,
        risk_amount=None,
        risk_percent=None,
        reason_codes=() if tradable else ("NO_CONFIRMED_SETUP",),
        data_time=LAST_CLOSED,
        last_closed_bar=LAST_CLOSED,
        data_age_seconds=0.0,
        freshness_status="FRESH",
        generated_at=BASE + timedelta(minutes=5),
        engine_version="test-v1",
    )


def bar(index: int, o: str, h: str, l: str, c: str, *, provider_id: str = "p") -> NormalizedCandle:
    open_time = BASE + timedelta(minutes=5 * (index + 1))
    return NormalizedCandle(
        provider_id=provider_id,
        symbol="XUSDT",
        interval="5m",
        open_time=open_time,
        close_time=open_time + timedelta(minutes=5) - timedelta(milliseconds=1),
        open=Decimal(o),
        high=Decimal(h),
        low=Decimal(l),
        close=Decimal(c),
        volume=Decimal("100"),
        closed=True,
    )


def test_outcome_win_after_separate_entry_bar():
    out = evaluate_signal_outcome(decision(), [bar(0, "101", "102", "99", "101"), bar(1, "110", "116", "109", "114")], evaluated_at=BASE + timedelta(hours=1))
    assert out.status == "WIN"
    assert out.outcome_r == Decimal("3")
    assert out.bars_to_entry == 1
    assert out.bars_in_trade == 2


def test_outcome_loss_after_entry():
    out = evaluate_signal_outcome(decision(), [bar(0, "101", "102", "99", "101"), bar(1, "99", "101", "94", "96")], evaluated_at=BASE + timedelta(hours=1))
    assert out.status == "LOSS"
    assert out.outcome_r == Decimal("-1")


def test_outcome_same_bar_target_and_stop_is_ambiguous():
    out = evaluate_signal_outcome(decision(), [bar(0, "101", "102", "99", "101"), bar(1, "100", "116", "94", "105")], evaluated_at=BASE + timedelta(hours=1))
    assert out.status == "AMBIGUOUS"
    assert out.reason == "TARGET_AND_STOP_TOUCHED_SAME_BAR"


def test_outcome_entry_and_exit_same_bar_is_ambiguous():
    out = evaluate_signal_outcome(decision(), [bar(0, "110", "116", "99", "114")], evaluated_at=BASE + timedelta(hours=1))
    assert out.status == "AMBIGUOUS"
    assert out.reason == "ENTRY_AND_EXIT_LEVEL_TOUCHED_SAME_BAR"


def test_outcome_pending_entry_without_explicit_horizon():
    out = evaluate_signal_outcome(decision(), [bar(0, "105", "110", "101", "106")], evaluated_at=BASE + timedelta(hours=1))
    assert out.status == "PENDING_ENTRY"


def test_outcome_expired_no_entry_at_explicit_horizon():
    candles = [bar(0, "105", "110", "101", "106"), bar(1, "106", "111", "102", "107")]
    out = evaluate_signal_outcome(decision(), candles, horizon_end=BASE + timedelta(minutes=15), evaluated_at=BASE + timedelta(hours=1))
    assert out.status == "EXPIRED_NO_ENTRY"


def test_no_trade_is_not_eligible_for_outcome_sample():
    out = evaluate_signal_outcome(decision(side="NO_TRADE"), [], evaluated_at=BASE + timedelta(hours=1))
    assert out.status == "NOT_ELIGIBLE"
    assert not out.binary_resolved


def test_outcome_rejects_cross_provider_future_bars():
    with pytest.raises(ValueError, match="provider_id"):
        evaluate_signal_outcome(decision(), [bar(0, "101", "102", "99", "101", provider_id="other")], evaluated_at=BASE + timedelta(hours=1))


def test_outcome_rejects_future_gap():
    candles = [bar(0, "101", "102", "99", "101"), bar(2, "101", "102", "99", "101")]
    with pytest.raises(ValueError, match="missing bars"):
        evaluate_signal_outcome(decision(), candles, evaluated_at=BASE + timedelta(hours=1))


def test_decision_fingerprint_is_deterministic():
    assert decision_fingerprint(decision()) == decision_fingerprint(decision())


def test_outcome_repository_roundtrip_and_update(tmp_path):
    path = tmp_path / "outcomes.db"
    repo = OutcomeRepository(path)
    try:
        pending = evaluate_signal_outcome(decision(), [bar(0, "105", "110", "101", "106")], evaluated_at=BASE + timedelta(minutes=10))
        repo.upsert(pending)
        assert repo.get(pending.decision_id).status == "PENDING_ENTRY"
        resolved = evaluate_signal_outcome(decision(), [bar(0, "101", "102", "99", "101"), bar(1, "110", "116", "109", "114")], evaluated_at=BASE + timedelta(hours=1))
        repo.upsert(resolved)
        loaded = repo.get(resolved.decision_id)
        assert loaded is not None and loaded.status == "WIN"
        assert repo.counts() == {"WIN": 1}
        assert [item.status for item in repo.list_binary_resolved()] == ["WIN"]
    finally:
        repo.close()
