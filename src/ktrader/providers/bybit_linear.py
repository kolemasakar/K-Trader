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
from ktrader.providers.parsers import CANONICAL_TO_BYBIT, parse_bybit_kline
from ktrader.providers.ws_transport import json_websocket_session

_INTERVAL_MAP = {
    "5m": "5",
    "15m": "15",
    "1h": "60",
    "4h": "240",
    "1d": "D",
}
_WS_URL = "wss://stream.bybit.com/v5/public/linear"


class BybitLinearProvider(MarketDataProvider):
    provider_id = "bybit_linear"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.http = PublicHttpClient(
            base_url="https://api.bybit.com",
            client=client,
        )

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider_id=self.provider_id,
            perpetual_derivatives=True,
            intervals=frozenset(_INTERVAL_MAP),
            quote_volume=True,
            trade_count=False,
            taker_buy_volume=False,
            book_ticker=True,
            open_interest=True,
            websocket_candles=True,
            max_kline_page_size=1000,
        )

    async def list_instruments(self) -> list[NormalizedInstrument]:
        result: list[NormalizedInstrument] = []
        cursor: str | None = None
        while True:
            params: dict[str, object] = {
                "category": "linear",
                "limit": 1000,
            }
            if cursor:
                params["cursor"] = cursor
            payload = await self.http.get_json(
                "/v5/market/instruments-info",
                params,
            )
            data = _result(payload)
            for raw in data.get("list", []):
                if raw.get("quoteCoin") != "USDT":
                    continue
                price_filter = raw.get("priceFilter", {})
                lot_filter = raw.get("lotSizeFilter", {})
                contract_type = (
                    "PERPETUAL"
                    if raw.get("contractType") == "LinearPerpetual"
                    else raw.get("contractType", "UNKNOWN")
                )
                status = (
                    "TRADING"
                    if raw.get("status") == "Trading"
                    else raw.get("status", "UNKNOWN").upper()
                )
                result.append(
                    NormalizedInstrument(
                        provider_id=self.provider_id,
                        symbol=raw["symbol"],
                        provider_symbol=raw["symbol"],
                        base_asset=raw["baseCoin"],
                        quote_asset=raw["quoteCoin"],
                        market_type="LINEAR_FUTURES",
                        contract_type=contract_type,
                        status=status,
                        price_tick=_decimal_or_none(
                            price_filter.get("tickSize")
                        ),
                        quantity_step=_decimal_or_none(
                            lot_filter.get("qtyStep")
                        ),
                    )
                )
            cursor = data.get("nextPageCursor") or None
            if not cursor:
                break
        return result

    async def get_tickers(self) -> list[NormalizedTicker]:
        payload = await self.http.get_json(
            "/v5/market/tickers",
            {"category": "linear"},
        )
        data = _result(payload)
        payload_time = (
            payload.get("time") if isinstance(payload, dict) else None
        )
        now = (
            utc_from_ms(payload_time)
            if payload_time
            else datetime.now(timezone.utc)
        )
        tickers: list[NormalizedTicker] = []
        for raw in data.get("list", []):
            if not raw.get("symbol", "").endswith("USDT"):
                continue
            tickers.append(
                NormalizedTicker(
                    provider_id=self.provider_id,
                    symbol=raw["symbol"],
                    timestamp=now,
                    last_price=Decimal(raw["lastPrice"]),
                    quote_volume_24h=_decimal_or_none(
                        raw.get("turnover24h")
                    ),
                    base_volume_24h=_decimal_or_none(
                        raw.get("volume24h")
                    ),
                    trade_count_24h=None,
                    bid_price=_decimal_or_none(raw.get("bid1Price")),
                    ask_price=_decimal_or_none(raw.get("ask1Price")),
                    open_interest=_decimal_or_none(
                        raw.get("openInterest")
                    ),
                )
            )
        return tickers

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
        if not 1 <= limit <= 1000:
            raise ValueError(
                "Bybit kline limit must be between 1 and 1000"
            )
        payload = await self.http.get_json(
            "/v5/market/kline",
            {
                "category": "linear",
                "symbol": provider_symbol,
                "interval": _INTERVAL_MAP[interval],
                "limit": limit,
            },
        )
        data = _result(payload)
        rows = data.get("list", [])
        interval_ms = _interval_ms(interval)
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        candles = [
            NormalizedCandle(
                provider_id=self.provider_id,
                symbol=instrument.symbol,
                interval=interval,
                open_time=utc_from_ms(row[0]),
                close_time=utc_from_ms(int(row[0]) + interval_ms - 1),
                open=Decimal(row[1]),
                high=Decimal(row[2]),
                low=Decimal(row[3]),
                close=Decimal(row[4]),
                volume=Decimal(row[5]),
                quote_volume=_decimal_or_none(row[6]),
                closed=(int(row[0]) + interval_ms) <= now_ms,
            )
            for row in reversed(rows)
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
        topics: list[str] = []
        raw_interval = CANONICAL_TO_BYBIT[interval]
        for instrument in instruments:
            if instrument.provider_id != self.provider_id:
                raise ValueError(
                    "All live instruments must belong to bybit_linear"
                )
            provider_symbol = (
                instrument.provider_symbol or instrument.symbol
            )
            symbol_map[provider_symbol] = instrument.symbol
            topics.append(
                f"kline.{raw_interval}.{provider_symbol}"
            )
        subscribe = {
            "op": "subscribe",
            "args": topics,
            "req_id": "ktrader-kline",
        }
        async for message in json_websocket_session(
            _WS_URL,
            subscribe_payloads=(subscribe,),
            heartbeat_payload={"op": "ping"},
            heartbeat_interval_seconds=20.0,
        ):
            event = parse_bybit_kline(
                message.payload,
                symbol_map=symbol_map,
                received_at=message.received_at,
                connection_id=message.connection_id,
            )
            if event is not None:
                yield event

    async def close(self) -> None:
        await self.http.close()


def _result(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ProviderError("Unexpected Bybit payload")
    if payload.get("retCode") != 0:
        raise ProviderError(
            f"Bybit API error {payload.get('retCode')}: "
            f"{payload.get('retMsg')}"
        )
    result = payload.get("result")
    if not isinstance(result, dict):
        raise ProviderError("Bybit payload has no result object")
    return result


def _decimal_or_none(value: object) -> Decimal | None:
    return None if value in (None, "") else Decimal(str(value))


def _interval_ms(interval: str) -> int:
    return {
        "5m": 300_000,
        "15m": 900_000,
        "1h": 3_600_000,
        "4h": 14_400_000,
        "1d": 86_400_000,
    }[interval]
