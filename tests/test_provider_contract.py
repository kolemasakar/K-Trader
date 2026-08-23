from decimal import Decimal

import httpx
import pytest

from ktrader.providers.binance_usdm import BinanceUSDMProvider
from ktrader.providers.bybit_linear import BybitLinearProvider


BINANCE_EXCHANGE = {
    "symbols": [
        {
            "symbol": "SUIUSDT",
            "baseAsset": "SUI",
            "quoteAsset": "USDT",
            "contractType": "PERPETUAL",
            "status": "TRADING",
            "filters": [
                {"filterType": "PRICE_FILTER", "tickSize": "0.0001"},
                {"filterType": "LOT_SIZE", "stepSize": "0.1"},
            ],
        }
    ]
}

BINANCE_TICKERS = [
    {
        "symbol": "SUIUSDT",
        "lastPrice": "0.8123",
        "volume": "1000000",
        "quoteVolume": "810000",
        "count": 12345,
        "closeTime": 1787472000000,
    }
]

BINANCE_KLINES = [
    [1787471700000, "0.80", "0.82", "0.79", "0.81", "1000", 1787471999999, "810", 100, "520", "421", "0"],
]

BYBIT_INSTRUMENTS = {
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "list": [
            {
                "symbol": "SUIUSDT",
                "baseCoin": "SUI",
                "quoteCoin": "USDT",
                "contractType": "LinearPerpetual",
                "status": "Trading",
                "priceFilter": {"tickSize": "0.0001"},
                "lotSizeFilter": {"qtyStep": "0.1"},
            }
        ],
        "nextPageCursor": "",
    },
}

BYBIT_TICKERS = {
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "list": [
            {
                "symbol": "SUIUSDT",
                "lastPrice": "0.8124",
                "turnover24h": "900000",
                "volume24h": "1100000",
                "bid1Price": "0.8123",
                "ask1Price": "0.8125",
                "openInterest": "500000",
            }
        ]
    },
}

BYBIT_KLINES = {
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "list": [
            ["1787471700000", "0.80", "0.82", "0.79", "0.81", "1000", "810"]
        ]
    },
}


def mock_client(provider: str) -> httpx.AsyncClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if provider == "binance":
            payloads = {
                "/fapi/v1/exchangeInfo": BINANCE_EXCHANGE,
                "/fapi/v1/ticker/24hr": BINANCE_TICKERS,
                "/fapi/v1/ticker/bookTicker": [{"symbol": "SUIUSDT", "bidPrice": "0.8122", "askPrice": "0.8124"}],
                "/fapi/v1/klines": BINANCE_KLINES,
            }
        else:
            payloads = {
                "/v5/market/instruments-info": BYBIT_INSTRUMENTS,
                "/v5/market/tickers": BYBIT_TICKERS,
                "/v5/market/kline": BYBIT_KLINES,
            }
        return httpx.Response(200, json=payloads[path])

    return httpx.AsyncClient(base_url="https://mock.test", transport=httpx.MockTransport(handler))


@pytest.mark.parametrize("provider_name", ["binance", "bybit"])
async def test_two_providers_satisfy_same_normalized_contract(provider_name: str):
    client = mock_client(provider_name)
    provider = (
        BinanceUSDMProvider(client=client)
        if provider_name == "binance"
        else BybitLinearProvider(client=client)
    )
    try:
        instruments = await provider.list_instruments()
        tickers = await provider.get_tickers()
        candles = await provider.get_candles(instruments[0], "5m", limit=1)
    finally:
        await client.aclose()

    assert len(instruments) == len(tickers) == len(candles) == 1
    instrument = instruments[0]
    ticker = tickers[0]
    candle = candles[0]

    assert instrument.symbol == ticker.symbol == candle.symbol == "SUIUSDT"
    assert instrument.quote_asset == "USDT"
    assert instrument.is_tradable_perpetual
    assert ticker.last_price > 0
    assert ticker.quote_volume_24h is not None
    assert candle.interval == "5m"
    assert candle.open == Decimal("0.80")
    assert candle.quote_volume == Decimal("810")
    assert candle.open_time.tzinfo is not None


async def test_provider_capabilities_keep_missing_fields_explicit():
    binance_client = httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})))
    bybit_client = httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})))
    try:
        assert BinanceUSDMProvider(client=binance_client).capabilities.taker_buy_volume is True
        assert BybitLinearProvider(client=bybit_client).capabilities.taker_buy_volume is False
    finally:
        await binance_client.aclose()
        await bybit_client.aclose()
