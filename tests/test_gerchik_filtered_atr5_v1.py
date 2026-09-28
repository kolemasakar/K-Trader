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
