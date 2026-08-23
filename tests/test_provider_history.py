from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json

import pytest

from ktrader.history import (
    build_history_dataset,
    collect_provider_history,
    load_history_dataset,
    write_history_dataset,
)
from ktrader.models import NormalizedCandle, NormalizedInstrument, ProviderCapabilities
from ktrader.providers.base import MarketDataProvider

UTC = timezone.utc
START = datetime(2026, 8, 1, tzinfo=UTC)


def instrument(provider_id: str = "fake") -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id=provider_id,
        symbol="SUIUSDT",
        provider_symbol="SUIUSDT",
        base_asset="SUI",
        quote_asset="USDT",
        market_type="LINEAR_FUTURES",
        contract_type="PERPETUAL",
        status="TRADING",
        price_tick=Decimal("0.0001"),
        quantity_step=Decimal("0.1"),
    )


def bar(index: int, *, provider_id: str = "fake", close: str = "1.00", closed: bool = True) -> NormalizedCandle:
    open_time = START + timedelta(minutes=5 * index)
    value = Decimal(close)
    return NormalizedCandle(
        provider_id=provider_id,
        symbol="SUIUSDT",
        interval="5m",
        open_time=open_time,
        close_time=open_time + timedelta(minutes=5) - timedelta(milliseconds=1),
        open=value,
        high=value + Decimal("0.01"),
        low=value - Decimal("0.01"),
        close=value,
        volume=Decimal("100"),
        quote_volume=Decimal("100"),
        closed=closed,
    )


class FakeHistoryProvider(MarketDataProvider):
    provider_id = "fake"

    def __init__(self, candles):
        self.candles = list(candles)
        self.requested_limits = []

    @property
    def capabilities(self):
        return ProviderCapabilities(
            provider_id=self.provider_id,
            perpetual_derivatives=True,
            intervals=frozenset({"5m"}),
            max_kline_page_size=10,
        )

    async def list_instruments(self):
        return [instrument()]

    async def get_tickers(self):
        return []

    async def get_candles(self, instrument, interval, *, limit):
        self.requested_limits.append(limit)
        return self.candles[-limit:]


def test_history_dataset_roundtrip_and_digest(tmp_path):
    dataset = build_history_dataset([bar(i) for i in range(5)], provider_symbol="SUIUSDT", requested_bars=5, fetched_at=START + timedelta(days=1))
    path = write_history_dataset(tmp_path / "history.jsonl", dataset)
    loaded = load_history_dataset(path)
    assert loaded.manifest.content_sha256 == dataset.manifest.content_sha256
    assert loaded.candles == dataset.candles
    assert loaded.manifest.source_kind == "provider"


def test_history_dataset_detects_content_tamper(tmp_path):
    dataset = build_history_dataset([bar(i) for i in range(3)], provider_symbol="SUIUSDT", fetched_at=START + timedelta(days=1))
    path = write_history_dataset(tmp_path / "history.jsonl", dataset)
    lines = path.read_text(encoding="utf-8").splitlines()
    payload = json.loads(lines[-1])
    payload["close"] = "1.005"
    lines[-1] = json.dumps(payload, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        load_history_dataset(path)


@pytest.mark.asyncio
async def test_history_collector_uses_latest_closed_bars_only():
    provider = FakeHistoryProvider([bar(i) for i in range(8)] + [bar(8, closed=False)])
    dataset = await collect_provider_history(provider, instrument(), "5m", max_bars=5, fetched_at=START + timedelta(days=1))
    assert provider.requested_limits == [6]
    assert dataset.manifest.candle_count == 5
    assert all(c.closed for c in dataset.candles)
    assert dataset.candles[-1].open_time == START + timedelta(minutes=35)


@pytest.mark.asyncio
async def test_history_collector_rejects_gap_and_excess_page_request():
    provider = FakeHistoryProvider([bar(0), bar(1), bar(3), bar(4)])
    with pytest.raises(ValueError, match="missing bars"):
        await collect_provider_history(provider, instrument(), "5m", max_bars=4, fetched_at=START + timedelta(days=1))
    with pytest.raises(ValueError, match="page capacity"):
        await collect_provider_history(provider, instrument(), "5m", max_bars=11, fetched_at=START + timedelta(days=1))
