from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Mapping

from ktrader.market.timeframes import datetime_from_ms, expected_close_time
from ktrader.models import NormalizedCandle
from ktrader.providers.live import LiveCandleEvent

BINANCE_INTERVALS = {"5m", "15m", "1h", "4h", "1d"}
BYBIT_TO_CANONICAL = {
    "5": "5m",
    "15": "15m",
    "60": "1h",
    "240": "4h",
    "D": "1d",
}
CANONICAL_TO_BYBIT = {
    value: key for key, value in BYBIT_TO_CANONICAL.items()
}


def parse_binance_kline(
    payload: object,
    *,
    symbol_map: Mapping[str, str],
    received_at: datetime,
    connection_id: int = 0,
) -> LiveCandleEvent | None:
    if not isinstance(payload, dict):
        return None
    if "data" in payload and isinstance(payload["data"], dict):
        payload = payload["data"]
    if payload.get("e") != "kline":
        return None
    raw = payload.get("k")
    if not isinstance(raw, dict):
        return None
    provider_symbol = str(raw.get("s") or payload.get("s") or "")
    canonical = symbol_map.get(provider_symbol)
    if canonical is None:
        return None
    interval = str(raw.get("i"))
    if interval not in BINANCE_INTERVALS:
        return None
    open_time = datetime_from_ms(int(raw["t"]))
    candle = NormalizedCandle(
        provider_id="binance_usdm",
        symbol=canonical,
        interval=interval,
        open_time=open_time,
        close_time=expected_close_time(open_time, interval),
        open=Decimal(str(raw["o"])),
        high=Decimal(str(raw["h"])),
        low=Decimal(str(raw["l"])),
        close=Decimal(str(raw["c"])),
        volume=Decimal(str(raw["v"])),
        quote_volume=_decimal_or_none(raw.get("q")),
        trade_count=_int_or_none(raw.get("n")),
        taker_buy_volume=_decimal_or_none(raw.get("V")),
        taker_buy_quote_volume=_decimal_or_none(raw.get("Q")),
        closed=bool(raw.get("x")),
    )
    event_ms = payload.get("E") or raw.get("T")
    event_time = (
        datetime_from_ms(int(event_ms))
        if event_ms is not None
        else received_at
    )
    return LiveCandleEvent(
        candle=candle,
        event_time=event_time,
        received_at=received_at,
        connection_id=connection_id,
        raw_topic=None,
    )


def parse_bybit_kline(
    payload: object,
    *,
    symbol_map: Mapping[str, str],
    received_at: datetime,
    connection_id: int = 0,
) -> LiveCandleEvent | None:
    if not isinstance(payload, dict):
        return None
    topic = payload.get("topic")
    if not isinstance(topic, str) or not topic.startswith("kline."):
        return None
    data = payload.get("data")
    if not isinstance(data, list) or not data:
        return None
    raw = data[0]
    if not isinstance(raw, dict):
        return None
    parts = topic.split(".", 2)
    if len(parts) != 3:
        return None
    _, raw_interval, provider_symbol = parts
    canonical = symbol_map.get(provider_symbol)
    interval = BYBIT_TO_CANONICAL.get(raw_interval)
    if canonical is None or interval is None:
        return None
    open_time = datetime_from_ms(int(raw["start"]))
    candle = NormalizedCandle(
        provider_id="bybit_linear",
        symbol=canonical,
        interval=interval,
        open_time=open_time,
        close_time=expected_close_time(open_time, interval),
        open=Decimal(str(raw["open"])),
        high=Decimal(str(raw["high"])),
        low=Decimal(str(raw["low"])),
        close=Decimal(str(raw["close"])),
        volume=Decimal(str(raw["volume"])),
        quote_volume=_decimal_or_none(raw.get("turnover")),
        trade_count=None,
        taker_buy_volume=None,
        taker_buy_quote_volume=None,
        closed=bool(raw.get("confirm")),
    )
    event_ms = payload.get("ts") or raw.get("timestamp")
    event_time = (
        datetime_from_ms(int(event_ms))
        if event_ms is not None
        else received_at
    )
    return LiveCandleEvent(
        candle=candle,
        event_time=event_time,
        received_at=received_at,
        connection_id=connection_id,
        raw_topic=topic,
    )


def _decimal_or_none(value: object) -> Decimal | None:
    return None if value in (None, "") else Decimal(str(value))


def _int_or_none(value: object) -> int | None:
    return None if value in (None, "") else int(value)
