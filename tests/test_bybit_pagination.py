import httpx

from ktrader.providers.bybit_linear import BybitLinearProvider


async def test_bybit_instrument_pagination():
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        cursor = request.url.params.get("cursor")
        symbol = "AAAUSDT" if not cursor else "BBBUSDT"
        next_cursor = "page2" if not cursor else ""
        return httpx.Response(
            200,
            json={
                "retCode": 0,
                "retMsg": "OK",
                "result": {
                    "list": [
                        {
                            "symbol": symbol,
                            "baseCoin": symbol.removesuffix("USDT"),
                            "quoteCoin": "USDT",
                            "contractType": "LinearPerpetual",
                            "status": "Trading",
                            "priceFilter": {"tickSize": "0.001"},
                            "lotSizeFilter": {"qtyStep": "1"},
                        }
                    ],
                    "nextPageCursor": next_cursor,
                },
            },
        )

    client = httpx.AsyncClient(base_url="https://mock.test", transport=httpx.MockTransport(handler))
    try:
        provider = BybitLinearProvider(client=client)
        items = await provider.list_instruments()
    finally:
        await client.aclose()

    assert calls == 2
    assert [x.symbol for x in items] == ["AAAUSDT", "BBBUSDT"]
