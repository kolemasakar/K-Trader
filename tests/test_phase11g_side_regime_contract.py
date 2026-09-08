from decimal import Decimal
from types import SimpleNamespace

import pytest

from ktrader.engine.scoring import context_strength, score_setup


def _regime(value: str):
    return SimpleNamespace(
        regime=value,
        by_interval={
            "1d": SimpleNamespace(regime=value),
            "4h": SimpleNamespace(regime=value),
            "1h": SimpleNamespace(regime=value),
        },
        strength_by_interval={
            "1d": SimpleNamespace(evidence_count=3),
            "4h": SimpleNamespace(evidence_count=3),
            "1h": SimpleNamespace(evidence_count=3),
        },
    )


def _candidate(side: str):
    level = SimpleNamespace(
        level_id="L1",
        provider_id="test",
        symbol="XUSDT",
        status="CONFIRMED",
        strength="STRONG",
    )
    trap = SimpleNamespace(
        confirmed=True,
        status="CONFIRMED",
        direction=side,
        level_id="L1",
        provider_id="test",
        symbol="XUSDT",
    )
    return SimpleNamespace(
        direction=side,
        setup_type="TRAP_LEVEL_CONFIRMATION",
        primary_level=level,
        trap=trap,
        vsa=None,
    )


def _geometry():
    return SimpleNamespace(
        atr_used_pct=Decimal("20"),
        rr=Decimal("3"),
    )


def _session():
    return SimpleNamespace(
        overlap=True,
        active_sessions=("LONDON", "NEW_YORK"),
    )


@pytest.mark.parametrize(
    ("side", "regime_value"),
    (
        ("LONG", "BULLISH"),
        ("SHORT", "BEARISH"),
    ),
)
def test_canonical_regime_matches_trading_side(side, regime_value):
    result = score_setup(
        _candidate(side),
        _geometry(),
        regime=_regime(regime_value),
        session=_session(),
        liquidity_rank=1,
        universe_size=10,
        liquidity_score=Decimal("1000"),
        freshness_stale=False,
    )

    assert "HTF_CONTEXT_MISMATCH" not in result.hard_rejects
    assert result.components["market_regime"] == 20
    assert result.grade == "A"


@pytest.mark.parametrize(
    ("side", "regime_value"),
    (
        ("LONG", "BULLISH"),
        ("SHORT", "BEARISH"),
    ),
)
def test_context_strength_uses_canonical_regime_vocabulary(side, regime_value):
    assert context_strength(_regime(regime_value), side) == "STRONG"


def test_opposite_canonical_regime_remains_hard_reject():
    result = score_setup(
        _candidate("LONG"),
        _geometry(),
        regime=_regime("BEARISH"),
        session=_session(),
        liquidity_rank=1,
        universe_size=10,
        liquidity_score=Decimal("1000"),
        freshness_stale=False,
    )

    assert "HTF_CONTEXT_MISMATCH" in result.hard_rejects
    assert result.components["market_regime"] == 0
    assert result.grade == "C"
