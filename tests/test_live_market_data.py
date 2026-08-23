from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from ktrader.market.aggregation import aggregate_closed_candles
from ktrader.market.live import LiveConfig, LiveMarketDataService, LiveSymbolState
from ktrader.market.reconcile import ReconciliationService
from ktrader.market.timeframes import expected_close_time
from ktrader.models import NormalizedCandle, NormalizedInstrument, ProviderCapabilities
from ktrader.providers.base import MarketDataProvider
from ktrader.providers.live import LiveCandleEvent
from ktrader.providers.parsers import parse_binance_kline, parse_bybit_kline
from ktrader.storage.sqlite import CandleRepository

UTC = timezone.utc


def candle(
    minute: int,
    *,
    interval: str = "5m",
    closed: bool = True,
    close: str | None = None,
    provider: str = "binance_usdm",
    symbol: str = "AAAUSDT",
) -> NormalizedCandle:
    open_time = datetime(2026, 8, 23, 9, minute, tzinfo=UTC)
    return NormalizedCandle(
        provider_id=provider,
        symbol=symbol,
        interval=interval,
        open_time=open_time,
        close_time=expected_close_time(open_time, interval),
        open=Decimal("1"),
        high=Decimal("2"),
        low=Decimal("0.5"),
        close=Decimal(close or "1.5"),
        volume=Decimal("10"),
        quote_volume=Decimal("15"),
        trade_count=2,
        taker_buy_volume=Decimal("4"),
        taker_buy_quote_volume=Decimal("6"),
        closed=closed,
    )


def instrument(provider: str = "binance_usdm") -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id=provider,
        symbol="AAAUSDT",
        provider_symbol="AAAUSDT",
        base_asset="AAA",
        quote_asset="USDT",
        market_type="LINEAR_FUTURES",
        contract_type="PERPETUAL",
        status="TRADING",
    )


class FakeProvider(MarketDataProvider):
    provider_id = "binance_usdm"

    def __init__(self, rows_by_interval=None) -> None:
        self.rows_by_interval = rows_by_interval or {}

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider_id=self.provider_id,
            perpetual_derivatives=True,
            intervals=frozenset({"5m", "15m", "1h", "4h", "1d"}),
            websocket_candles=True,
            max_kline_page_size=1500,
        )

    async def list_instruments(self):
        return [instrument()]

    async def get_tickers(self):
        return []

    async def get_candles(self, inst, interval, *, limit):
        return self.rows_by_interval.get(interval, [])[-limit:]


def test_binance_parser_closed():
    received = datetime(2026, 8, 23, 9, 5, tzinfo=UTC)
    payload = {
        "e": "kline",
        "E": 1787475900000,
        "s": "AAAUSDT",
        "k": {
            "t": 1787475600000,
            "T": 1787475899999,
            "s": "AAAUSDT",
            "i": "5m",
            "o": "1",
            "h": "2",
            "l": "0.5",
            "c": "1.5",
            "v": "10",
            "q": "15",
            "n": 3,
            "V": "4",
            "Q": "6",
            "x": True,
        },
    }
    event = parse_binance_kline(
        payload,
        symbol_map={"AAAUSDT": "AAAUSDT"},
        received_at=received,
    )
    assert event is not None and event.candle.closed
    assert event.candle.trade_count == 3
    assert event.candle.taker_buy_volume == Decimal("4")


def test_bybit_parser_open_and_close_boundary():
    received = datetime(2026, 8, 23, 9, 5, tzinfo=UTC)
    payload = {
        "topic": "kline.5.AAAUSDT",
        "ts": 1787475900000,
        "data": [
            {
                "start": 1787475600000,
                "end": 1787475899999,
                "interval": "5",
                "open": "1",
                "high": "2",
                "low": "0.5",
                "close": "1.5",
                "volume": "10",
                "turnover": "15",
                "confirm": False,
                "timestamp": 1787475890000,
            }
        ],
    }
    event = parse_bybit_kline(
        payload,
        symbol_map={"AAAUSDT": "AAAUSDT"},
        received_at=received,
    )
    assert event is not None and event.candle.closed is False
    assert event.candle.quote_volume == Decimal("15")
    assert event.candle.close_time == expected_close_time(
        event.candle.open_time,
        "5m",
    )


def test_aggregate_15m_preserves_volume_fields():
    rows = [candle(0), candle(5), candle(10, close="1.8")]
    aggregated = aggregate_closed_candles(
        rows,
        parent_interval="15m",
    )
    assert aggregated.open == Decimal("1")
    assert aggregated.close == Decimal("1.8")
    assert aggregated.volume == Decimal("30")
    assert aggregated.trade_count == 6
    assert aggregated.taker_buy_quote_volume == Decimal("18")


def test_storage_tracks_aggregate_source(tmp_path):
    repo = CandleRepository(tmp_path / "x.db")
    aggregated = aggregate_closed_candles(
        [candle(0), candle(5), candle(10)],
        parent_interval="15m",
    )
    repo.upsert_many(
        [aggregated],
        source_kind="aggregate",
        derived_from_interval="5m",
    )
    assert repo.source_info(
        "binance_usdm",
        "AAAUSDT",
        "15m",
        aggregated.open_time,
    ) == ("aggregate", "5m")


@pytest.mark.asyncio
async def test_live_open_not_persisted_closed_persisted_and_aggregated(tmp_path):
    repo = CandleRepository(tmp_path / "x.db")
    provider = FakeProvider()
    service = LiveMarketDataService(
        repo,
        config=LiveConfig(reconcile_every_closed_bars=0),
    )
    inst = instrument()
    repo.upsert_many([candle(0), candle(5)])

    await service.process_event(
        provider,
        inst,
        LiveCandleEvent.now(candle(10, closed=False)),
    )
    assert repo.count("binance_usdm", "AAAUSDT", "5m") == 2

    await service.process_event(
        provider,
        inst,
        LiveCandleEvent.now(candle(10, closed=True)),
    )
    assert repo.count("binance_usdm", "AAAUSDT", "5m") == 3
    parent = repo.latest("binance_usdm", "AAAUSDT", "15m")
    assert parent is not None and parent.open_time.minute == 0
    assert repo.source_info(
        "binance_usdm",
        "AAAUSDT",
        "15m",
        parent.open_time,
    ) == ("aggregate", "5m")


@pytest.mark.asyncio
async def test_reconciliation_overwrites_aggregate_with_provider(tmp_path):
    repo = CandleRepository(tmp_path / "x.db")
    aggregated = aggregate_closed_candles(
        [candle(0), candle(5), candle(10)],
        parent_interval="15m",
    )
    repo.upsert_many(
        [aggregated],
        source_kind="aggregate",
        derived_from_interval="5m",
    )
    values = {
        field: getattr(aggregated, field)
        for field in aggregated.__dataclass_fields__
    }
    values["close"] = Decimal("1.7")
    native = NormalizedCandle(**values)
    provider = FakeProvider({"15m": [native]})

    result = await ReconciliationService(repo).reconcile_interval(
        provider,
        instrument(),
        "15m",
        limit=1,
    )
    assert result.corrected == 1
    assert repo.latest(
        "binance_usdm",
        "AAAUSDT",
        "15m",
    ).close == Decimal("1.7")
    assert repo.source_info(
        "binance_usdm",
        "AAAUSDT",
        "15m",
        aggregated.open_time,
    ) == ("provider", None)


@pytest.mark.asyncio
async def test_live_gap_recovery_uses_rest(tmp_path):
    repo = CandleRepository(tmp_path / "x.db")
    repo.upsert_many([candle(0)])
    provider = FakeProvider(
        {"5m": [candle(0), candle(5), candle(10), candle(15)]}
    )
    service = LiveMarketDataService(
        repo,
        config=LiveConfig(
            reconcile_every_closed_bars=0,
            reconcile_lookback=10,
        ),
    )
    await service.process_event(
        provider,
        instrument(),
        LiveCandleEvent.now(candle(15)),
    )
    stored = repo.load_recent(
        "binance_usdm",
        "AAAUSDT",
        "5m",
        limit=10,
    )
    assert [item.open_time.minute for item in stored] == [0, 5, 10, 15]
    assert service.state_for(instrument()).gap_recoveries == 1


def test_state_stale_boundary():
    state = LiveSymbolState(
        "p",
        "s",
        last_event_at=datetime(2026, 8, 23, 9, 0, tzinfo=UTC),
    )
    assert not state.stale(
        now=datetime(2026, 8, 23, 9, 1, tzinfo=UTC),
        stale_after_seconds=90,
    )
    assert state.stale(
        now=datetime(2026, 8, 23, 9, 2, tzinfo=UTC),
        stale_after_seconds=90,
    )


def test_storage_schema_v1_migrates_to_v2(tmp_path):
    path = tmp_path / "legacy.db"
    connection = sqlite3.connect(path)
    connection.execute(
        """CREATE TABLE candles (
        provider_id TEXT NOT NULL, symbol TEXT NOT NULL, interval TEXT NOT NULL,
        open_time_ms INTEGER NOT NULL, close_time_ms INTEGER NOT NULL,
        open_price TEXT NOT NULL, high_price TEXT NOT NULL,
        low_price TEXT NOT NULL, close_price TEXT NOT NULL,
        volume TEXT NOT NULL, quote_volume TEXT, trade_count INTEGER,
        taker_buy_volume TEXT, taker_buy_quote_volume TEXT,
        closed INTEGER NOT NULL, ingested_at_ms INTEGER NOT NULL,
        PRIMARY KEY(provider_id, symbol, interval, open_time_ms))"""
    )
    connection.commit()
    connection.close()

    repo = CandleRepository(path)
    columns = {
        row["name"]
        for row in repo._connection.execute(
            "PRAGMA table_info(candles)"
        ).fetchall()
    }
    assert {"source_kind", "derived_from_interval"} <= columns
    assert repo._connection.execute(
        "PRAGMA user_version"
    ).fetchone()[0] == 2


@pytest.mark.asyncio
async def test_duplicate_closed_event_is_idempotent(tmp_path):
    repo = CandleRepository(tmp_path / "x.db")
    provider = FakeProvider()
    service = LiveMarketDataService(
        repo,
        config=LiveConfig(reconcile_every_closed_bars=0),
    )
    inst = instrument()
    event = LiveCandleEvent.now(candle(0))

    await service.process_event(provider, inst, event)
    await service.process_event(provider, inst, event)

    assert repo.count("binance_usdm", "AAAUSDT", "5m") == 1
    assert service.state_for(inst).closed_bars_seen == 1
