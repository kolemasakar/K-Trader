from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.market.timeframes import expected_close_time
from ktrader.market.validation import (
    CandleValidationError,
    FreshnessPolicy,
    assess_freshness,
    find_gaps,
    validate_candle,
)
from ktrader.models import NormalizedCandle
from ktrader.storage.sqlite import CandleRepository


def candle(open_time: datetime, interval: str = "5m", **overrides) -> NormalizedCandle:
    values = dict(
        provider_id="fake",
        symbol="TESTUSDT",
        interval=interval,
        open_time=open_time,
        close_time=expected_close_time(open_time, interval),
        open=Decimal("1.2300"),
        high=Decimal("1.2500"),
        low=Decimal("1.2200"),
        close=Decimal("1.2400"),
        volume=Decimal("100.5000"),
        quote_volume=Decimal("123.456700"),
        trade_count=42,
        taker_buy_volume=Decimal("51.25"),
        taker_buy_quote_volume=Decimal("63.001"),
        closed=True,
    )
    values.update(overrides)
    return NormalizedCandle(**values)


def test_sqlite_wal_and_decimal_roundtrip(tmp_path):
    repo = CandleRepository(tmp_path / "market.db")
    assert repo.journal_mode == "wal"
    item = candle(datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc))
    assert repo.upsert_many([item]) == 1
    loaded = repo.load_recent("fake", "TESTUSDT", "5m", limit=1)[0]
    assert str(loaded.open) == "1.2300"
    assert str(loaded.quote_volume) == "123.456700"
    assert loaded == item
    repo.close()


def test_upsert_is_idempotent_and_updates_same_bar(tmp_path):
    repo = CandleRepository(tmp_path / "market.db")
    open_time = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    repo.upsert_many([candle(open_time)])
    repo.upsert_many([candle(open_time, close=Decimal("1.2450"))])
    assert repo.count("fake", "TESTUSDT", "5m") == 1
    assert repo.latest("fake", "TESTUSDT", "5m").close == Decimal("1.2450")
    repo.close()


def test_find_gaps_reports_missing_count():
    start = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    items = [candle(start), candle(start + timedelta(minutes=10))]
    gaps = find_gaps(items, "5m")
    assert len(gaps) == 1
    assert gaps[0].missing_count == 1


def test_validation_rejects_misaligned_and_invalid_ohlc():
    bad_time = candle(datetime(2026, 8, 23, 12, 1, tzinfo=timezone.utc))
    with pytest.raises(CandleValidationError, match="aligned"):
        validate_candle(bad_time)

    good_time = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    bad_price = candle(good_time, high=Decimal("1.23"), close=Decimal("1.24"))
    with pytest.raises(CandleValidationError, match="high"):
        validate_candle(bad_price)


def test_freshness_policy_is_interval_relative():
    open_time = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    latest = candle(open_time)
    policy = FreshnessPolicy(max_age_intervals=2.0)
    fresh = assess_freshness(
        latest,
        policy=policy,
        now=datetime(2026, 8, 23, 12, 8, tzinfo=timezone.utc),
    )
    stale = assess_freshness(
        latest,
        policy=policy,
        now=datetime(2026, 8, 23, 12, 16, tzinfo=timezone.utc),
    )
    assert fresh.stale is False
    assert stale.stale is True
