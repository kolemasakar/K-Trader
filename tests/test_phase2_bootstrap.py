from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.market.bootstrap import BootstrapError, HistoryPlan, MTFBootstrapService
from ktrader.market.timeframes import expected_close_time, interval_seconds
from ktrader.market.validation import FreshnessPolicy
from ktrader.models import NormalizedCandle, NormalizedInstrument, ProviderCapabilities
from ktrader.providers.base import MarketDataProvider
from ktrader.storage.sqlite import CandleRepository


class FakeProvider(MarketDataProvider):
    provider_id = "fake"

    def __init__(self, now: datetime, *, gap_interval: str | None = None, stale: bool = False):
        self.now = now
        self.gap_interval = gap_interval
        self.stale = stale
        self.requests: list[tuple[str, int]] = []

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider_id=self.provider_id,
            perpetual_derivatives=True,
            intervals=frozenset({"5m", "15m", "1h", "4h", "1d"}),
            max_kline_page_size=1000,
        )

    async def list_instruments(self):
        return []

    async def get_tickers(self):
        return []

    async def get_candles(self, instrument, interval, *, limit):
        self.requests.append((interval, limit))
        seconds = interval_seconds(interval)
        epoch = int(self.now.timestamp())
        current_open_epoch = epoch - (epoch % seconds)
        if self.stale:
            current_open_epoch -= seconds * 10
        current_open = datetime.fromtimestamp(current_open_epoch, tz=timezone.utc)
        first = current_open - timedelta(seconds=seconds * (limit - 1))
        items = []
        for index in range(limit):
            open_time = first + timedelta(seconds=seconds * index)
            closed = open_time + timedelta(seconds=seconds) <= self.now
            items.append(
                NormalizedCandle(
                    provider_id=self.provider_id,
                    symbol=instrument.symbol,
                    interval=interval,
                    open_time=open_time,
                    close_time=expected_close_time(open_time, interval),
                    open=Decimal("1.00"),
                    high=Decimal("1.10"),
                    low=Decimal("0.90"),
                    close=Decimal("1.05"),
                    volume=Decimal("100"),
                    quote_volume=Decimal("105"),
                    closed=closed,
                )
            )
        if self.gap_interval == interval and len(items) >= 3:
            del items[1]
        return items


def instrument() -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id="fake",
        symbol="TESTUSDT",
        provider_symbol="TESTUSDT",
        base_asset="TEST",
        quote_asset="USDT",
        market_type="LINEAR_FUTURES",
        contract_type="PERPETUAL",
        status="TRADING",
    )


@pytest.mark.asyncio
async def test_bootstrap_persists_only_closed_target_bars_atomically(tmp_path):
    now = datetime(2026, 8, 23, 12, 2, tzinfo=timezone.utc)
    provider = FakeProvider(now)
    repo = CandleRepository(tmp_path / "market.db")
    service = MTFBootstrapService(repo, freshness_policy=FreshnessPolicy(2.0))
    plan = HistoryPlan({"15m": 2, "5m": 3})

    result = await service.bootstrap(provider, instrument(), plan=plan, now=now)

    assert provider.requests == [("15m", 3), ("5m", 4)]
    assert result.interval_counts == {"15m": 2, "5m": 3}
    assert result.stored_total == 5
    assert repo.count("fake", "TESTUSDT", "15m") == 2
    assert repo.count("fake", "TESTUSDT", "5m") == 3
    assert all(c.closed for c in repo.load_recent("fake", "TESTUSDT", "5m", limit=10))
    assert repo.latest_bootstrap_run("fake", "TESTUSDT")["status"] == "SUCCESS"
    repo.close()


@pytest.mark.asyncio
async def test_bootstrap_covers_all_canonical_timeframes(tmp_path):
    now = datetime(2026, 8, 23, 12, 2, tzinfo=timezone.utc)
    provider = FakeProvider(now)
    repo = CandleRepository(tmp_path / "market.db")
    service = MTFBootstrapService(repo)
    plan = HistoryPlan({"1d": 2, "4h": 2, "1h": 2, "15m": 2, "5m": 2})

    result = await service.bootstrap(provider, instrument(), plan=plan, now=now)
    assert result.interval_counts == {key: 2 for key in plan.interval_counts}
    assert repo.interval_counts("fake", "TESTUSDT") == {key: 2 for key in plan.interval_counts}
    repo.close()


@pytest.mark.asyncio
async def test_gap_failure_writes_no_partial_snapshot(tmp_path):
    now = datetime(2026, 8, 23, 12, 2, tzinfo=timezone.utc)
    provider = FakeProvider(now, gap_interval="5m")
    repo = CandleRepository(tmp_path / "market.db")
    service = MTFBootstrapService(repo)
    plan = HistoryPlan({"15m": 2, "5m": 3})

    with pytest.raises(BootstrapError):
        await service.bootstrap(provider, instrument(), plan=plan, now=now)

    assert repo.count("fake", "TESTUSDT", "15m") == 0
    assert repo.count("fake", "TESTUSDT", "5m") == 0
    assert repo.latest_bootstrap_run("fake", "TESTUSDT")["status"] == "FAILED"
    repo.close()


@pytest.mark.asyncio
async def test_stale_history_fails_closed_without_persistence(tmp_path):
    now = datetime(2026, 8, 23, 12, 2, tzinfo=timezone.utc)
    provider = FakeProvider(now, stale=True)
    repo = CandleRepository(tmp_path / "market.db")
    service = MTFBootstrapService(repo, freshness_policy=FreshnessPolicy(2.0))

    with pytest.raises(BootstrapError, match="Stale"):
        await service.bootstrap(
            provider,
            instrument(),
            plan=HistoryPlan({"5m": 3}),
            now=now,
        )

    assert repo.count("fake", "TESTUSDT", "5m") == 0
    repo.close()
