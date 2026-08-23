from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest

from ktrader.market.timeframes import datetime_to_ms
from ktrader.models import NormalizedInstrument
from ktrader.providers.binance_usdm import BinanceUSDMProvider
from ktrader.providers.bybit_linear import BybitLinearProvider


UTC = timezone.utc


def instrument(provider_id: str) -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id=provider_id,
        symbol="SUIUSDT",
        provider_symbol="SUIUSDT",
        base_asset="SUI",
        quote_asset="USDT",
        market_type="LINEAR_FUTURES",
        contract_type="PERPETUAL",
        status="TRADING",
    )


@pytest.mark.asyncio
async def test_binance_historical_page_uses_end_time_cursor():
    end_time = datetime(2026, 8, 20, 12, tzinfo=UTC)
    open_ms = datetime_to_ms(datetime(2026, 8, 20, 11, 55, tzinfo=UTC))

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/fapi/v1/klines"
        assert request.url.params["endTime"] == str(datetime_to_ms(end_time))
        assert request.url.params["limit"] == "2"
        return httpx.Response(200, json=[[
            open_ms,
            "0.80",
            "0.82",
            "0.79",
            "0.81",
            "1000",
            open_ms + 300_000 - 1,
            "810",
            100,
            "520",
            "421",
            "0",
        ]])

    client = httpx.AsyncClient(base_url="https://mock.test", transport=httpx.MockTransport(handler))
    provider = BinanceUSDMProvider(client=client)
    try:
        rows = await provider.get_historical_candles(
            instrument("binance_usdm"), "5m", limit=2, end_time=end_time
        )
    finally:
        await client.aclose()
    assert len(rows) == 1
    assert rows[0].symbol == "SUIUSDT"
    assert rows[0].closed is True


@pytest.mark.asyncio
async def test_bybit_historical_page_uses_end_cursor_and_normalizes_order():
    end_time = datetime(2026, 8, 20, 12, tzinfo=UTC)
    first = datetime_to_ms(datetime(2026, 8, 20, 11, 50, tzinfo=UTC))
    second = datetime_to_ms(datetime(2026, 8, 20, 11, 55, tzinfo=UTC))

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v5/market/kline"
        assert request.url.params["end"] == str(datetime_to_ms(end_time))
        assert request.url.params["limit"] == "2"
        return httpx.Response(200, json={
            "retCode": 0,
            "retMsg": "OK",
            "result": {
                "list": [
                    [str(second), "0.81", "0.83", "0.80", "0.82", "100", "82"],
                    [str(first), "0.80", "0.82", "0.79", "0.81", "90", "73"],
                ]
            },
        })

    client = httpx.AsyncClient(base_url="https://mock.test", transport=httpx.MockTransport(handler))
    provider = BybitLinearProvider(client=client)
    try:
        rows = await provider.get_historical_candles(
            instrument("bybit_linear"), "5m", limit=2, end_time=end_time
        )
    finally:
        await client.aclose()
    assert [row.open_time for row in rows] == sorted(row.open_time for row in rows)
    assert rows[0].open_time < rows[1].open_time
    assert all(row.closed for row in rows)
