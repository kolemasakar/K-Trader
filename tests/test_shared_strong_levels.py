"""Shared-level invariants for all approved Gerchik models."""
import pytest
from ktrader.shared_strong_levels import STRATEGIES, shared_levels


def level(**changes):
    value = dict(price="100", timeframe="D1", side="SUPPORT",
                 known_at_ms=100, source_id="witness-1", strength="STRONG",
                 selection_status="STRONG_CONFIRMED")
    value.update(changes)
    return value


@pytest.mark.parametrize("strategy", sorted(STRATEGIES))
def test_same_level_for_every_strategy(strategy):
    assert shared_levels([level()], strategy=strategy, as_of_ms=100)[0].price == 100


@pytest.mark.parametrize("strategy", sorted(STRATEGIES))
def test_future_level_is_not_visible(strategy):
    assert shared_levels([level(known_at_ms=101)], strategy=strategy, as_of_ms=100) == ()


def test_unqualified_candidates_never_promoted():
    assert shared_levels([level(selection_status="RESEARCH_CANDIDATE")],
                         strategy="S2A", as_of_ms=100) == ()


def test_deduplication_is_stable():
    levels = [level(source_id="z"), level(source_id="a")]
    assert shared_levels(levels, strategy="S1", as_of_ms=100)[0].source_id == "a"


def test_reject_invalid_level_and_strategy():
    with pytest.raises(ValueError):
        shared_levels([level(timeframe="M5")], strategy="S1", as_of_ms=100)
    with pytest.raises(ValueError):
        shared_levels([], strategy="CHANNEL", as_of_ms=100)
