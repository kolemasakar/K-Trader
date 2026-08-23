from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.models import NormalizedCandle
from ktrader.indicators import (
    atr,
    atr5d,
    atr_used_pct,
    build_indicator_snapshot,
    ema,
    latest_volume_stats,
    ma50_200,
    sma,
    true_range,
)

UTC = timezone.utc


def make_candles(n, *, interval="1d", ranges=None, volumes=None, quote=True):
    seconds = {"1d": 86400, "4h": 14400, "1h": 3600, "15m": 900, "5m": 300}[interval]
    start = datetime(2025, 1, 1, tzinfo=UTC)
    result = []
    previous = Decimal("100")
    for index in range(n):
        open_time = start + timedelta(seconds=seconds * index)
        candle_range = Decimal(str(ranges[index] if ranges else 3))
        open_price = previous
        low = open_price - Decimal("1")
        high = low + candle_range
        close = low + (candle_range / Decimal("2"))
        volume = Decimal(str(volumes[index] if volumes else 100 + index))
        result.append(
            NormalizedCandle(
                provider_id="test",
                symbol="XUSDT",
                interval=interval,
                open_time=open_time,
                close_time=open_time + timedelta(seconds=seconds) - timedelta(milliseconds=1),
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
                quote_volume=(volume * close if quote else None),
                closed=True,
            )
        )
        previous = close
    return result


def test_true_range_includes_gap():
    candle = make_candles(1)[0]
    assert true_range(candle, Decimal("90")) == candle.high - Decimal("90")


def test_wilder_atr_constant_range():
    assert atr(make_candles(30)) == Decimal("3")


def test_atr5d_skips_high_and_low_abnormal_without_replacement():
    ranges = [3] * 30
    ranges[-1] = 10
    ranges[-2] = Decimal("0.5")
    result = atr5d(make_candles(30, ranges=ranges))
    assert len(result.valid_ranges) == 5
    assert Decimal("10") not in result.valid_ranges
    assert Decimal("0.5") not in result.valid_ranges
    assert result.rejected_high >= 1
    assert result.rejected_low >= 1
    assert len(set(result.valid_open_times)) == 5


def test_sma_and_ma50_200():
    values = [Decimal(index) for index in range(1, 201)]
    assert sma(values, period=50) == Decimal("175.5")
    assert ma50_200(make_candles(200)).method == "sma"


def test_ema_seed_and_update():
    values = [Decimal(index) for index in range(1, 6)]
    assert ema(values, period=3) == Decimal("4")


def test_volume_baseline_excludes_current_bar():
    volumes = [Decimal("100")] * 20 + [Decimal("300")]
    stats = latest_volume_stats(make_candles(21, volumes=volumes), window=20)
    assert stats.average_volume == Decimal("100")
    assert stats.relative_volume == Decimal("3")


def test_relative_quote_volume_unavailable_if_not_confirmed():
    stats = latest_volume_stats(make_candles(21, quote=False), window=20)
    assert stats.relative_quote_volume is None


@pytest.mark.parametrize(
    ("distance", "expected"),
    [
        ("1.19", "STRONG"),
        ("1.2", "ACCEPTABLE"),
        ("2.4", "ACCEPTABLE"),
        ("2.41", "LATE_REJECT"),
    ],
)
def test_atr_used_boundaries(distance, expected):
    assert atr_used_pct(Decimal(distance), Decimal("3")).classification == expected


def test_indicator_snapshot_returns_ma_atr_volume():
    snapshot = build_indicator_snapshot(make_candles(220, interval="1h"))
    assert snapshot.interval == "1h"
    assert snapshot.atr14 > 0
    assert snapshot.ma50 > 0
    assert snapshot.ma200 > 0
    assert snapshot.volume.relative_volume > 0
