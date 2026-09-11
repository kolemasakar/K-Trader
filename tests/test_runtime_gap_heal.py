from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.market.timeframes import expected_close_time, interval_seconds
from ktrader.models import NormalizedCandle, NormalizedInstrument
from ktrader.runtime.analyzer import EngineSymbolAnalyzer
from ktrader.runtime.models import RuntimeScannerConfig
from ktrader.storage.sqlite import CandleRepository

UTC = timezone.utc
NOW = datetime(2026, 9, 11, 7, 20, tzinfo=UTC)


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


def series(interval: str, count: int, *, gapped: bool = False):
    seconds = interval_seconds(interval)
    epoch = int(NOW.timestamp())
    current_open = epoch - (epoch % seconds)
    last_closed_open = datetime.fromtimestamp(current_open - seconds, tz=UTC)
    needed = count + (1 if gapped else 0)
    first = last_closed_open - timedelta(seconds=seconds * (needed - 1))
    rows = []
    for index in range(needed):
        open_time = first + timedelta(seconds=seconds * index)
        rows.append(
            NormalizedCandle(
                provider_id="fake",
                symbol="TESTUSDT",
                interval=interval,
                open_time=open_time,
                close_time=expected_close_time(open_time, interval),
                open=Decimal("1"),
                high=Decimal("1.1"),
                low=Decimal("0.9"),
                close=Decimal("1.05"),
                volume=Decimal("100"),
                closed=True,
            )
        )
    if gapped:
        del rows[len(rows) // 2]
    return rows


class Provider:
    provider_id = "fake"


class BootstrapStub:
    def __init__(self):
        self.calls = []

    async def bootstrap(self, provider, inst, *, plan, now):
        self.calls.append((provider.provider_id, inst.symbol, plan, now))


@pytest.mark.asyncio
async def test_recent_gap_triggers_bootstrap_even_when_count_and_freshness_pass(tmp_path):
    repo = CandleRepository(tmp_path / "market.db")
    config = RuntimeScannerConfig()
    for interval, count in config.history.interval_counts.items():
        repo.upsert_many(series(interval, count, gapped=interval == "15m"))

    analyzer = EngineSymbolAnalyzer(repo, config=config)
    stub = BootstrapStub()
    analyzer.bootstrap = stub

    await analyzer._ensure_ready(Provider(), instrument(), now=NOW)

    assert len(stub.calls) == 1
    assert stub.calls[0][0:2] == ("fake", "TESTUSDT")
    repo.close()


@pytest.mark.asyncio
async def test_contiguous_recent_history_does_not_bootstrap(tmp_path):
    repo = CandleRepository(tmp_path / "market.db")
    config = RuntimeScannerConfig()
    for interval, count in config.history.interval_counts.items():
        repo.upsert_many(series(interval, count))

    analyzer = EngineSymbolAnalyzer(repo, config=config)
    stub = BootstrapStub()
    analyzer.bootstrap = stub

    await analyzer._ensure_ready(Provider(), instrument(), now=NOW)

    assert stub.calls == []
    repo.close()
