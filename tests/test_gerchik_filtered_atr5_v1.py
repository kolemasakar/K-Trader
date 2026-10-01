"""Synthetic deterministic tests; not a substitute for historical validation."""
from datetime import date, timedelta
import pytest
from scripts.research.gerchik_filtered_atr5_v1 import DailyBar, InsufficientHistory, filtered_atr5

def bars(ranges):
    return [DailyBar((date(2026, 9, 28) - timedelta(days=i)).isoformat(), float(x), 0.)
            for i, x in enumerate(ranges)]

def test_normal():
    result = filtered_atr5(bars([10] * 12))
    assert result["atr5"] == 10 and not result["rejected"]

def test_first_large_slide():
    result = filtered_atr5(bars([40] + [10] * 12))
    assert result["atr5"] == 10 and result["rejected"][0]["reason"] == "LARGE"

def test_first_small_slide():
    result = filtered_atr5(bars([1] + [10] * 12))
    assert result["atr5"] == 10 and result["rejected"][0]["reason"] == "SMALL"

def test_older_replacements():
    result = filtered_atr5(bars([10, 40, 10, 1] + [10] * 15))
    assert result["atr5"] == 10
    assert [item["reason"] for item in result["rejected"]] == ["LARGE", "SMALL"]

def test_exact_thresholds():
    assert filtered_atr5(bars([20] + [7.5] * 4 + [10] * 12))["rejected"][0]["reason"] == "LARGE"
    assert filtered_atr5(bars([2] + [7] * 4 + [10] * 12))["rejected"][0]["reason"] == "SMALL"

def test_insufficient():
    with pytest.raises(InsufficientHistory):
        filtered_atr5(bars([10] * 4))

def test_duplicate():
    data = bars([10] * 8)
    data[1] = data[0]
    with pytest.raises(ValueError):
        filtered_atr5(data)


def test_thresholds_are_inclusive_with_candidate_in_reference():
    # Candidate-inclusive five-bar reference: (x + 4*10)/5.
    # x=16 -> reference=11.2, not large; x=80 -> reference=24, large.
    # Exact large boundary solves x = 2*(x+40)/5 -> x = 80/3.
    large = 80.0 / 3.0
    result = filtered_atr5(bars([large] + [10] * 15))
    assert result["rejected"][0]["reason"] == "LARGE"
    # Exact small boundary solves x = (x+40)/15 -> x = 20/7.
    small = 20.0 / 7.0
    result = filtered_atr5(bars([small] + [10] * 15))
    assert result["rejected"][0]["reason"] == "SMALL"


def test_accepted_are_five_distinct_completed_bars():
    result = filtered_atr5(bars([40, 10, 10, 1] + [10] * 15))
    accepted = result["accepted"]
    assert len(accepted) == 5
    assert len({item["timestamp"] for item in accepted}) == 5
    assert all(item["timestamp"] <= bars([40])[0].timestamp for item in accepted)
    assert result["inspected"] == len(accepted) + len(result["rejected"])


def test_rejects_non_descending_timestamps():
    data = bars([10] * 9)
    data[0], data[1] = data[1], data[0]
    with pytest.raises(ValueError, match="newest-to-oldest"):
        filtered_atr5(data)


def test_insufficient_older_replacements_fails_closed():
    with pytest.raises(InsufficientHistory):
        filtered_atr5(bars([10] * 5))


def test_causal_prefix_invariance():
    # Appending older observations must not alter an already-resolved window.
    prefix = [40, 10, 10, 1] + [10] * 9
    first = filtered_atr5(bars(prefix))
    extended = filtered_atr5(bars(prefix + [100, 1, 200, 2, 100]))
    assert first == extended


def test_consecutive_large_anomalies_replaced():
    result = filtered_atr5(bars([100, 100] + [10] * 14))
    assert [r["reason"] for r in result["rejected"][:2]] == ["LARGE", "LARGE"]
    assert result["atr5"] == 10


def test_book_boundary_values_and_nearby_values():
    # Candidate-inclusive initial five-bar reference; exact boundary cases.
    large = 80 / 3
    small = 20 / 7
    assert filtered_atr5(bars([large] + [10] * 15))["rejected"][0]["reason"] == "LARGE"
    assert filtered_atr5(bars([small] + [10] * 15))["rejected"][0]["reason"] == "SMALL"
    assert not filtered_atr5(bars([large - 0.01] + [10] * 15))["rejected"]
    assert not filtered_atr5(bars([small + 0.01] + [10] * 15))["rejected"]
