from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from datetime import datetime, timezone
from decimal import Decimal

import httpx

from ktrader.models import (
    NormalizedCandle,
    NormalizedInstrument,
    NormalizedTicker,
    ProviderCapabilities,
    utc_from_ms,
)
from ktrader.providers.base import MarketDataProvider, ProviderError
from ktrader.providers.http import PublicHttpClient
from ktrader.providers.live import LiveCandleEvent
from ktrader.providers.parsers import parse_binance_kline
from ktrader.providers.ws_transport import json_websocket_session

_INTERVALS = frozenset({"5m", "15m", "1h", "4h", "1d"})
_WS_URL = "wss://fstream.binance.com/market/stream"


class BinanceUSDMProvider(MarketDataProvider):
    provider_id = "binance_usdm"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.http = PublicHttpClient(
            base_url="https://fapi.binance.com",
            client=client,
        )

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider_id=self.provider_id,
            perpetual_derivatives=True,
            intervals=_INTERVALS,
            quote_volume=True,
            trade_count=True,
            taker_buy_volume=True,
            book_ticker=True,
            open_interest=True,
            websocket_candles=True,
            max_kline_page_size=1500,
        )

    async def list_instruments(self) -> list[NormalizedInstrument]:
        payload = await self.http.get_json("/fapi/v1/exchangeInfo")
        result: list[NormalizedInstrument] = []
        for raw in payload.get("symbols", []):
            filters = {
                item.get("filterType"): item
                for item in raw.get("filters", [])
            }
            price_filter = filters.get("PRICE_FILTER", {})
            lot_filter = filters.get("LOT_SIZE", {})
            result.append(
                NormalizedInstrument(
                    provider_id=self.provider_id,
                    symbol=raw["symbol"],
                    provider_symbol=raw["symbol"],
                    base_asset=raw["baseAsset"],
                    quote_asset=raw["quoteAsset"],
                    market_type="LINEAR_FUTURES",
                    contract_type=raw.get("contractType", "UNKNOWN"),
                    status=raw.get("status", "UNKNOWN"),
                    price_tick=_decimal_or_none(
                        price_filter.get("tickSize")
                    ),
                    quantity_step=_decimal_or_none(
                        lot_filter.get("stepSize")
                    ),
                )
            )
        return result

    async def get_tickers(self) -> list[NormalizedTicker]:
        payload = await self.http.get_json("/fapi/v1/ticker/24hr")
        books = await self.http.get_json("/fapi/v1/ticker/bookTicker")
        now = datetime.now(timezone.utc)
        if not isinstance(payload, list) or not isinstance(books, list):
            raise ProviderError("Unexpected Binance ticker payload")
        book_by_symbol = {raw.get("symbol"): raw for raw in books}
        return [
            NormalizedTicker(
                provider_id=self.provider_id,
                symbol=raw["symbol"],
                timestamp=(
                    utc_from_ms(raw["closeTime"])
                    if raw.get("closeTime")
                    else now
                ),
                last_price=Decimal(raw["lastPrice"]),
                quote_volume_24h=_decimal_or_none(
                    raw.get("quoteVolume")
                ),
                base_volume_24h=_decimal_or_none(raw.get("volume")),
                trade_count_24h=_int_or_none(raw.get("count")),
                bid_price=_decimal_or_none(
                    book_by_symbol.get(raw["symbol"], {}).get("bidPrice")
                ),
                ask_price=_decimal_or_none(
                    book_by_symbol.get(raw["symbol"], {}).get("askPrice")
                ),
            )
            for raw in payload
        ]

    async def get_candles(
        self,
        instrument: NormalizedInstrument,
        interval: str,
        *,
        limit: int,
    ) -> list[NormalizedCandle]:
        self.validate_interval(interval)
        if instrument.provider_id != self.provider_id:
            raise ValueError(
                f"Instrument provider {instrument.provider_id!r} "
                f"does not match {self.provider_id!r}"
            )
        provider_symbol = instrument.provider_symbol or instrument.symbol
        if not 1 <= limit <= 1500:
            raise ValueError(
                "Binance kline limit must be between 1 and 1500"
            )
        rows = await self.http.get_json(
            "/fapi/v1/klines",
            {
                "symbol": provider_symbol,
                "interval": interval,
                "limit": limit,
            },
        )
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        candles = [
            NormalizedCandle(
                provider_id=self.provider_id,
                symbol=instrument.symbol,
                interval=interval,
                open_time=utc_from_ms(row[0]),
                close_time=utc_from_ms(row[6]),
                open=Decimal(row[1]),
                high=Decimal(row[2]),
                low=Decimal(row[3]),
                close=Decimal(row[4]),
                volume=Decimal(row[5]),
                quote_volume=_decimal_or_none(row[7]),
                trade_count=_int_or_none(row[8]),
                taker_buy_volume=_decimal_or_none(row[9]),
                taker_buy_quote_volume=_decimal_or_none(row[10]),
                closed=int(row[6]) < now_ms,
            )
            for row in rows
        ]
        self.ensure_chronological(candles)
        return candles

    async def stream_candles(
        self,
        instruments: Sequence[NormalizedInstrument],
        interval: str = "5m",
    ) -> AsyncIterator[LiveCandleEvent]:
        self.validate_interval(interval)
        if not instruments:
            return
        symbol_map: dict[str, str] = {}
        streams: list[str] = []
        for instrument in instruments:
            if instrument.provider_id != self.provider_id:
                raise ValueError(
                    "All live instruments must belong to binance_usdm"
                )
            provider_symbol = (
                instrument.provider_symbol or instrument.symbol
            )
            symbol_map[provider_symbol] = instrument.symbol
            streams.append(
                f"{provider_symbol.lower()}@kline_{interval}"
            )
        subscribe = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": "ktrader-kline",
        }
        async for message in json_websocket_session(
            _WS_URL,
            subscribe_payloads=(subscribe,),
        ):
            event = parse_binance_kline(
                message.payload,
                symbol_map=symbol_map,
                received_at=message.received_at,
                connection_id=message.connection_id,
            )
            if event is not None:
                yield event

    async def close(self) -> None:
        await self.http.close()


def _decimal_or_none(value: object) -> Decimal | None:
    if value in (None, ""):
        return None
    return Decimal(str(value))


def _int_or_none(value: object) -> int | None:
    if value in (None, ""):
        return None
    return int(value)
