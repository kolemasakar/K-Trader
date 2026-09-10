from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.market.bootstrap import BootstrapError
from ktrader.market.timeframes import expected_close_time, interval_seconds
from ktrader.models import NormalizedCandle, NormalizedInstrument, ProviderCapabilities
from ktrader.providers.base import MarketDataProvider
from ktrader.runtime.analyzer import EngineSymbolAnalyzer
from ktrader.runtime.models import RuntimeScannerConfig
from ktrader.storage.sqlite import CandleRepository

UTC = timezone.utc


class ShortHistoryProvider(MarketDataProvider):
    provider_id = "fake"

    def __init__(self, now: datetime) -> None:
        self.now = now
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
        current_open_epoch = int(self.now.timestamp())
        current_open_epoch -= current_open_epoch % seconds
        current_open = datetime.fromtimestamp(current_open_epoch, tz=UTC)
        count = 10 if interval == "1d" else limit
        first = current_open - timedelta(seconds=seconds * count)
        return [
            NormalizedCandle(
                provider_id=self.provider_id,
                symbol=instrument.symbol,
                interval=interval,
                open_time=first + timedelta(seconds=seconds * index),
                close_time=expected_close_time(
                    first + timedelta(seconds=seconds * index), interval
                ),
                open=Decimal("1"),
                high=Decimal("1.1"),
                low=Decimal("0.9"),
                close=Decimal("1.05"),
                volume=Decimal("100"),
                closed=True,
            )
            for index in range(count)
        ]


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
async def test_insufficient_d1_failure_defers_retry_until_next_utc_day(tmp_path):
    repo = CandleRepository(tmp_path / "market.db")
    failed_at = datetime(2026, 9, 10, 3, 0, tzinfo=UTC)
    repo.record_bootstrap_run(
        provider_id="fake",
        symbol="TESTUSDT",
        started_at=failed_at,
        completed_at=failed_at,
        status="FAILED",
        interval_counts={},
        error="BootstrapError: Insufficient closed 1d bars: required=250, received=10",
    )
    provider = ShortHistoryProvider(failed_at)
    analyzer = EngineSymbolAnalyzer(repo, config=RuntimeScannerConfig())

    with pytest.raises(
        BootstrapError,
        match=r"retry deferred until 2026-09-11T00:00:00\+00:00",
    ):
        await analyzer._ensure_ready(
            provider, instrument(), now=failed_at + timedelta(hours=2)
        )

    assert provider.requests == []
    assert repo.latest_bootstrap_run("fake", "TESTUSDT")["id"] == 1

    provider.now = datetime(2026, 9, 11, 0, 1, tzinfo=UTC)
    with pytest.raises(BootstrapError, match="Insufficient closed 1d bars"):
        await analyzer._ensure_ready(provider, instrument(), now=provider.now)

    assert provider.requests == [("1d", 251)]
    assert repo.latest_bootstrap_run("fake", "TESTUSDT")["id"] == 2
    repo.close()


@pytest.mark.asyncio
async def test_non_history_failure_does_not_activate_d1_backoff(tmp_path):
    repo = CandleRepository(tmp_path / "market.db")
    failed_at = datetime(2026, 9, 10, 3, 0, tzinfo=UTC)
    repo.record_bootstrap_run(
        provider_id="fake",
        symbol="TESTUSDT",
        started_at=failed_at,
        completed_at=failed_at,
        status="FAILED",
        interval_counts={},
        error="BootstrapError: stale runtime 5m series",
    )
    provider = ShortHistoryProvider(failed_at + timedelta(hours=1))
    analyzer = EngineSymbolAnalyzer(repo, config=RuntimeScannerConfig())

    with pytest.raises(BootstrapError, match="Insufficient closed 1d bars"):
        await analyzer._ensure_ready(
            provider, instrument(), now=failed_at + timedelta(hours=1)
        )

    assert provider.requests == [("1d", 251)]
    repo.close()
