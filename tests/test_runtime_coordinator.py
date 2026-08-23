from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from ktrader.api.state import ApiReadModel, ScannerRuntimeStatus
from ktrader.engine.models import TradingDecision
from ktrader.models import NormalizedInstrument, NormalizedTicker, ProviderCapabilities
from ktrader.providers.base import MarketDataProvider, ProviderError
from ktrader.runtime.analyzer import SymbolAnalysisResult
from ktrader.runtime.coordinator import ScannerCoordinator
from ktrader.runtime.models import RuntimeScannerConfig
from ktrader.storage.sqlite import CandleRepository

UTC = timezone.utc
NOW = datetime(2026, 8, 23, 11, 0, tzinfo=UTC)


class FakeProvider(MarketDataProvider):
    def __init__(self, provider_id="fake", symbols=("AAAUSDT", "BBBUSDT"), fail=False):
        self.provider_id = provider_id
        self.symbols = symbols
        self.fail = fail

    @property
    def capabilities(self):
        return ProviderCapabilities(self.provider_id, True, frozenset({"5m", "15m", "1h", "4h", "1d"}), websocket_candles=True, max_kline_page_size=500)

    async def list_instruments(self):
        if self.fail:
            raise ProviderError("offline")
        return [NormalizedInstrument(self.provider_id, symbol, symbol[:-4], "USDT", "USDT_PERPETUAL", "PERPETUAL", "TRADING", Decimal("0.001"), Decimal("1"), symbol) for symbol in self.symbols]

    async def get_tickers(self):
        if self.fail:
            raise ProviderError("offline")
        return [NormalizedTicker(self.provider_id, symbol, NOW, Decimal("1"), quote_volume_24h=Decimal(str(1000000-index*1000)), bid_price=Decimal("0.999"), ask_price=Decimal("1.001")) for index, symbol in enumerate(self.symbols)]

    async def get_candles(self, instrument, interval, *, limit):
        raise AssertionError("fake analyzer should own symbol analysis")

    async def stream_candles(self, instruments, interval="5m"):
        while True:
            await asyncio.sleep(3600)
            if False:
                yield None


class FakeAnalyzer:
    def __init__(self, fail_symbol=None):
        self.fail_symbol = fail_symbol

    async def analyze(self, provider, item, *, liquidity_rank, universe_size, now):
        if item.instrument.symbol == self.fail_symbol:
            raise RuntimeError("symbol failure")
        instrument = item.instrument
        decision = TradingDecision(
            provider_id=instrument.provider_id,
            exchange=instrument.provider_id,
            canonical_symbol=instrument.symbol,
            provider_symbol=instrument.provider_symbol or instrument.symbol,
            market_type=instrument.market_type,
            side="NO_TRADE",
            grade="C",
            setup_score=0,
            raw_score=0,
            setup_type="NO_SETUP",
            market_regime="RANGE",
            trend_context="RANGE",
            liquidity_rank=liquidity_rank,
            liquidity_score=item.liquidity_score,
            sessions=(),
            session_overlap=False,
            strength="N/A",
            primary_level_id=None,
            primary_level_strength=None,
            trap_state=None,
            vsa_events=(),
            entry=None,
            luft=None,
            stop=None,
            target=None,
            rr=None,
            atr5d=Decimal("0.1"),
            atr_used_pct=None,
            atr_state=None,
            position_size=None,
            risk_amount=None,
            risk_percent=None,
            reason_codes=("NO_CONFIRMED_SETUP",),
            data_time=NOW,
            last_closed_bar=NOW,
            data_age_seconds=0.0,
            freshness_status="FRESH",
            generated_at=now,
            engine_version="test",
        )
        return SymbolAnalysisResult((decision,), ())


@pytest.mark.asyncio
async def test_cycle_publishes_universe_and_no_trade_analysis():
    repo = CandleRepository(":memory:")
    model = ApiReadModel()
    coordinator = ScannerCoordinator([FakeProvider()], repo, model, config=RuntimeScannerConfig(analysis_limit=2), analyzer=FakeAnalyzer())
    result = await coordinator.run_once(now=NOW)
    assert result.symbols_ready == 2
    assert model.get_status().data_ready is True
    assert model.resolve_analysis("AAAUSDT", provider_id="fake").reason_codes == ("NO_CONFIRMED_SETUP",)
    await coordinator.stop()
    repo.close()


@pytest.mark.asyncio
async def test_symbol_failure_is_isolated_and_cycle_is_degraded():
    repo = CandleRepository(":memory:")
    model = ApiReadModel()
    coordinator = ScannerCoordinator([FakeProvider()], repo, model, config=RuntimeScannerConfig(analysis_limit=2), analyzer=FakeAnalyzer(fail_symbol="BBBUSDT"))
    result = await coordinator.run_once(now=NOW)
    assert result.symbols_ready == 1
    assert result.symbols_failed == 1
    assert model.get_status().status == "DEGRADED"
    assert model.resolve_analysis("AAAUSDT", provider_id="fake").side == "NO_TRADE"
    await coordinator.stop()
    repo.close()


@pytest.mark.asyncio
async def test_provider_failure_falls_back_without_cross_provider_snapshot():
    repo = CandleRepository(":memory:")
    model = ApiReadModel()
    coordinator = ScannerCoordinator([FakeProvider("bad", fail=True), FakeProvider("good", symbols=("CCCUSDT",))], repo, model, config=RuntimeScannerConfig(analysis_limit=1), analyzer=FakeAnalyzer())
    result = await coordinator.run_once(now=NOW)
    assert result.provider_id == "good"
    assert {item.instrument.provider_id for item in model.list_universe()} == {"good"}
    assert "bad" in (model.get_status().last_error or "")
    await coordinator.stop()
    repo.close()


def test_atomic_publish_replaces_old_provider_state():
    model = ApiReadModel()
    old_provider = FakeProvider("old", symbols=("AAAUSDT",))
    new_provider = FakeProvider("new", symbols=("BBBUSDT",))
    old_item = asyncio.run(__import__("ktrader.market.service", fromlist=["load_universe"]).load_universe(old_provider, RuntimeScannerConfig().universe)).candidates[0]
    new_item = asyncio.run(__import__("ktrader.market.service", fromlist=["load_universe"]).load_universe(new_provider, RuntimeScannerConfig().universe)).candidates[0]
    model.publish_cycle(status=ScannerRuntimeStatus(status="READY", provider_id="old", data_ready=True), universe=(old_item,), candle_series=(), decisions=())
    model.publish_cycle(status=ScannerRuntimeStatus(status="READY", provider_id="new", data_ready=True), universe=(new_item,), candle_series=(), decisions=())
    assert [item.instrument.provider_id for item in model.list_universe()] == ["new"]
