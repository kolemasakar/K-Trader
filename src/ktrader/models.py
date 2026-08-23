from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Mapping


def utc_from_ms(value: int | str) -> datetime:
    return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)


@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    provider_id: str
    perpetual_derivatives: bool
    intervals: frozenset[str]
    quote_volume: bool = False
    trade_count: bool = False
    taker_buy_volume: bool = False
    book_ticker: bool = False
    open_interest: bool = False
    websocket_candles: bool = False
    max_kline_page_size: int | None = None


@dataclass(frozen=True, slots=True)
class NormalizedInstrument:
    provider_id: str
    symbol: str
    base_asset: str
    quote_asset: str
    market_type: str
    contract_type: str
    status: str
    price_tick: Decimal | None = None
    quantity_step: Decimal | None = None
    provider_symbol: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def instrument_id(self) -> str:
        return f"{self.provider_id}:{self.symbol}"

    @property
    def is_tradable_perpetual(self) -> bool:
        return self.status == "TRADING" and self.contract_type == "PERPETUAL"


@dataclass(frozen=True, slots=True)
class NormalizedTicker:
    provider_id: str
    symbol: str
    timestamp: datetime
    last_price: Decimal
    quote_volume_24h: Decimal | None = None
    base_volume_24h: Decimal | None = None
    trade_count_24h: int | None = None
    bid_price: Decimal | None = None
    ask_price: Decimal | None = None
    open_interest: Decimal | None = None

    @property
    def spread(self) -> Decimal | None:
        if self.bid_price is None or self.ask_price is None:
            return None
        return self.ask_price - self.bid_price

    @property
    def spread_bps(self) -> Decimal | None:
        if self.bid_price is None or self.ask_price is None:
            return None
        mid = (self.bid_price + self.ask_price) / Decimal("2")
        if mid <= 0:
            return None
        return (self.ask_price - self.bid_price) / mid * Decimal("10000")


@dataclass(frozen=True, slots=True)
class NormalizedCandle:
    provider_id: str
    symbol: str
    interval: str
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    quote_volume: Decimal | None = None
    trade_count: int | None = None
    taker_buy_volume: Decimal | None = None
    taker_buy_quote_volume: Decimal | None = None
    closed: bool = True
