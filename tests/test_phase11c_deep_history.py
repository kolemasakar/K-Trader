from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.history import collect_deep_provider_history
from ktrader.models import NormalizedCandle, NormalizedInstrument, ProviderCapabilities
from ktrader.providers.base import MarketDataProvider, ProviderError


UTC = timezone.utc


def candle(index: int, *, provider_id: str = "fake", interval: str = "5m") -> NormalizedCandle:
    open_time = datetime(2026, 8, 20, tzinfo=UTC) + timedelta(minutes=5 * index)
    return NormalizedCandle(
        provider_id=provider_id,
        symbol="SUIUSDT",
        interval=interval,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=5) - timedelta(milliseconds=1),
        open=Decimal("1.00"),
        high=Decimal("1.02"),
        low=Decimal("0.99"),
        close=Decimal("1.01"),
        volume=Decimal("100"),
        closed=True,
    )


class PagedProvider(MarketDataProvider):
    provider_id = "fake"

    def __init__(self, candles: list[NormalizedCandle]) -> None:
        self.candles = candles
        self.cursors: list[datetime] = []

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider_id=self.provider_id,
            perpetual_derivatives=True,
            intervals=frozenset({"5m"}),
            max_kline_page_size=3,
        )

    async def list_instruments(self):
        return []

    async def get_tickers(self):
        return []

    async def get_candles(self, instrument, interval, *, limit):
        return self.candles[-limit:]

    async def get_historical_candles(self, instrument, interval, *, limit, end_time):
        self.cursors.append(end_time)
        eligible = [item for item in self.candles if item.open_time <= end_time]
        return eligible[-limit:]


class NoPagingProvider(PagedProvider):
    async def get_historical_candles(self, instrument, interval, *, limit, end_time):
        return await MarketDataProvider.get_historical_candles(
            self, instrument, interval, limit=limit, end_time=end_time
        )


def instrument() -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id="fake",
        symbol="SUIUSDT",
        provider_symbol="SUIUSDT",
        base_asset="SUI",
        quote_asset="USDT",
        market_type="LINEAR_FUTURES",
        contract_type="PERPETUAL",
        status="TRADING",
    )


@pytest.mark.asyncio
async def test_deep_history_pages_backward_and_returns_exact_depth():
    provider = PagedProvider([candle(index) for index in range(10)])
    as_of = datetime(2026, 8, 21, tzinfo=UTC)
    dataset = await collect_deep_provider_history(
        provider,
        instrument(),
        "5m",
        max_bars=7,
        fetched_at=as_of,
    )
    assert len(dataset.candles) == 7
    assert dataset.candles[0].open_time == candle(3).open_time
    assert dataset.candles[-1].open_time == candle(9).open_time
    assert len(provider.cursors) >= 3
    assert all(later < earlier for earlier, later in zip(provider.cursors, provider.cursors[1:]))


@pytest.mark.asyncio
async def test_deep_history_rejects_insufficient_depth():
    provider = PagedProvider([candle(index) for index in range(4)])
    with pytest.raises(ProviderError, match="insufficient deep history"):
        await collect_deep_provider_history(
            provider,
            instrument(),
            "5m",
            max_bars=7,
            fetched_at=datetime(2026, 8, 21, tzinfo=UTC),
            max_pages=5,
        )


@pytest.mark.asyncio
async def test_deep_history_rejects_cross_provider_page():
    rows = [candle(index) for index in range(5)]
    rows[-1] = candle(4, provider_id="other")
    provider = PagedProvider(rows)
    with pytest.raises(ProviderError, match="identity mismatch"):
        await collect_deep_provider_history(
            provider,
            instrument(),
            "5m",
            max_bars=3,
            fetched_at=datetime(2026, 8, 21, tzinfo=UTC),
        )


@pytest.mark.asyncio
async def test_deep_history_rejects_provider_without_paging_contract():
    provider = NoPagingProvider([candle(index) for index in range(5)])
    with pytest.raises(ProviderError, match="does not support deep historical pagination"):
        await collect_deep_provider_history(
            provider,
            instrument(),
            "5m",
            max_bars=3,
            fetched_at=datetime(2026, 8, 21, tzinfo=UTC),
        )


@pytest.mark.asyncio
async def test_deep_history_rejects_gap_after_page_merge():
    rows = [candle(index) for index in range(8) if index != 4]
    provider = PagedProvider(rows)
    with pytest.raises(ValueError):
        await collect_deep_provider_history(
            provider,
            instrument(),
            "5m",
            max_bars=7,
            fetched_at=datetime(2026, 8, 21, tzinfo=UTC),
        )
