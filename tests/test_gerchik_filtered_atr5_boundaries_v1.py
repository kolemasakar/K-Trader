"""Boundary, causality and failure-mode tests for iterative five-selected-bar ATR5."""
from datetime import date, timedelta
import math
import pytest
from scripts.research.gerchik_filtered_atr5_v1 import DailyBar, InsufficientHistory, filtered_atr5


def bars(ranges):
    return [DailyBar((date(2026, 9, 28) - timedelta(days=i)).isoformat(), float(x), 0.0)
            for i, x in enumerate(ranges)]


def test_large_threshold_equality_rejected():
    result = filtered_atr5(bars([20] + [7.5] * 4 + [10] * 10))
    assert result["rejected"][0]["reason"] == "LARGE"


def test_small_threshold_equality_rejected():
    result = filtered_atr5(bars([2] + [7] * 4 + [10] * 10))
    assert result["rejected"][0]["reason"] == "SMALL"


def test_just_inside_large_threshold_is_accepted():
    result = filtered_atr5(bars([19.99] + [7.5] * 4 + [10] * 10))
    assert result["accepted"][0]["range"] == pytest.approx(19.99)


def test_just_inside_small_threshold_is_accepted():
    result = filtered_atr5(bars([2.01] + [7] * 4 + [10] * 10))
    assert result["accepted"][0]["range"] == pytest.approx(2.01)


def test_exactly_five_completed_normal_bars_suffice():
    assert filtered_atr5(bars([10] * 5))["atr5"] == 10
    with pytest.raises(InsufficientHistory):
        filtered_atr5(bars([10] * 4))


def test_lookback_cap_is_enforced_when_replacement_needed():
    data = bars([40] + [10] * 19)
    with pytest.raises(InsufficientHistory):
        filtered_atr5(data, max_lookback=5)
    assert filtered_atr5(data, max_lookback=6)["atr5"] == 10


def test_equal_large_bars_are_normal_relative_to_their_own_mean():
    # Five equally sized bars are NOT outliers under the owner iterative rule.
    assert filtered_atr5(bars([40] * 5 + [10] * 3), max_lookback=8)["atr5"] == 40


def test_invalid_input_ranges():
    for high, low in [(1, 1), (0, 1), (math.inf, 0), (math.nan, 0)]:
        invalid = bars([10] * 10)
        invalid[2] = DailyBar(invalid[2].timestamp, high, low)
        with pytest.raises(ValueError):
            filtered_atr5(invalid)


def test_unsorted_timestamps_rejected():
    invalid = bars([10] * 10)
    invalid[0], invalid[1] = invalid[1], invalid[0]
    with pytest.raises(ValueError, match="newest-to-oldest"):
        filtered_atr5(invalid)


def test_no_future_bars_affect_past_asof():
    data = bars([10, 40, 10, 1] + [10] * 15)
    asof = filtered_atr5(data)
    newer = [DailyBar("2026-09-29", 999, 0)]
    later = filtered_atr5(newer + data)
    assert asof["atr5"] == filtered_atr5((newer + data)[1:])["atr5"]
    assert asof["accepted"] == filtered_atr5((newer + data)[1:])["accepted"]
    assert later["rejected"][0]["timestamp"] == "2026-09-29"
    assert later["accepted"][0]["timestamp"] == asof["accepted"][0]["timestamp"]


def test_result_deterministic():
    data = bars([10, 40, 10, 1] + [10] * 15)
    assert filtered_atr5(data) == filtered_atr5(data)
