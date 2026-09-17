from __future__ import annotations

import math
import os
from datetime import datetime
from typing import Any

import httpx

from ktrader.providers.base import ProviderError


class KAIMT4MarketContextAdapter:
    """Read-only adapter for canonical MT4 market-context bundles from K_AI."""

    provider_id = "kai_mt4"
    endpoint = "/v1/market-context/acquire"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_token: str | None = None,
        timeout_seconds: float = 55.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        resolved_url = base_url or os.getenv("KAI_MT4_BASE_URL", "http://127.0.0.1:8765")
        self.base_url = resolved_url.rstrip("/")
        self.api_token = api_token or os.getenv("KAI_MT4_API_TOKEN")
        self._owns_client = client is None
        headers = {"User-Agent": "K-Trader/0.1 read-only-kai-mt4"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        self.client = client or httpx.AsyncClient(timeout=timeout_seconds, headers=headers)

    async def acquire_market_context(
        self,
        symbol: str,
        market: str,
        *,
        require_m15: bool = False,
    ) -> dict[str, Any]:
        symbol = str(symbol or "").strip()
        market = str(market or "").strip().lower()
        if not symbol or not market:
            raise ValueError("symbol and market are required")

        try:
            response = await self.client.post(
                f"{self.base_url}{self.endpoint}",
                json={"symbol": symbol, "market": market},
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"K_AI MT4 market-context request failed: {exc}") from exc

        self.validate_market_context(
            payload,
            expected_symbol=symbol,
            expected_market=market,
            require_m15=require_m15,
        )
        return payload

    @classmethod
    def validate_market_context(
        cls,
        payload: Any,
        *,
        expected_symbol: str | None = None,
        expected_market: str | None = None,
        require_m15: bool = False,
    ) -> None:
        if not isinstance(payload, dict):
            raise ProviderError("K_AI market context must be a JSON object")

        schema = str(payload.get("schema_version") or "")
        expected_scopes = {
            "1.0": {"D1", "H1", "M5"},
            "1.1": {"D1", "H1", "M15", "M5"},
        }.get(schema)
        if expected_scopes is None:
            raise ProviderError(f"Unsupported K_AI market-context schema: {schema or '<missing>'}")
        if require_m15 and schema != "1.1":
            raise ProviderError("M15 requires K_AI MARKET_CONTEXT schema 1.1")

        required_equal = {
            "report_type": "MARKET_CONTEXT",
            "source_name": "MT4",
            "data_quality_flag": "VALID",
            "time_source": "BrokerServer",
        }
        for field, expected in required_equal.items():
            if payload.get(field) != expected:
                raise ProviderError(f"Invalid K_AI market-context {field}: {payload.get(field)!r}")
        if payload.get("closed_bars_only") is not True:
            raise ProviderError("K_AI market context must contain closed bars only")

        symbol = str(payload.get("symbol") or "")
        market = str(payload.get("market") or "").lower()
        if expected_symbol is not None and symbol != expected_symbol:
            raise ProviderError(f"K_AI symbol mismatch: {symbol!r} != {expected_symbol!r}")
        if expected_market is not None and market != expected_market.lower():
            raise ProviderError(f"K_AI market mismatch: {market!r} != {expected_market.lower()!r}")
        for field in ("run_id", "captured_at", "last_tick_time"):
            if not str(payload.get(field) or "").strip():
                raise ProviderError(f"K_AI market context is missing {field}")

        cls._validate_market_facts(payload)

        scopes = payload.get("scopes")
        if not isinstance(scopes, dict) or set(scopes) != expected_scopes:
            raise ProviderError(
                f"K_AI schema {schema} must contain exactly {sorted(expected_scopes)} scopes"
            )
        for scope in expected_scopes:
            cls._validate_scope(scope, scopes[scope])

    @staticmethod
    def _finite_number(value: Any, *, field: str) -> float:
        if isinstance(value, bool):
            raise ProviderError(f"K_AI {field} must be numeric, not boolean")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ProviderError(f"K_AI {field} must be numeric") from exc
        if not math.isfinite(number):
            raise ProviderError(f"K_AI {field} must be finite")
        return number

    @classmethod
    def _validate_market_facts(cls, payload: dict[str, Any]) -> None:
        required = (
            "bid", "ask", "spread", "digits", "point", "stop_level",
            "freeze_level", "tick_value", "tick_size", "contract_size",
            "trade_allowed", "terminal_connected", "market_open",
        )
        missing = [field for field in required if field not in payload]
        if missing:
            raise ProviderError(f"K_AI market context missing market facts: {', '.join(missing)}")

        bid = cls._finite_number(payload["bid"], field="market fact bid")
        ask = cls._finite_number(payload["ask"], field="market fact ask")
        spread = cls._finite_number(payload["spread"], field="market fact spread")
        point = cls._finite_number(payload["point"], field="market fact point")
        stop_level = cls._finite_number(payload["stop_level"], field="market fact stop_level")
        freeze_level = cls._finite_number(payload["freeze_level"], field="market fact freeze_level")
        tick_value = cls._finite_number(payload["tick_value"], field="market fact tick_value")
        tick_size = cls._finite_number(payload["tick_size"], field="market fact tick_size")
        contract_size = cls._finite_number(payload["contract_size"], field="market fact contract_size")

        digits_raw = payload["digits"]
        if isinstance(digits_raw, bool):
            raise ProviderError("K_AI market fact digits must be an integer")
        try:
            digits = int(digits_raw)
            digits_numeric = float(digits_raw)
        except (TypeError, ValueError) as exc:
            raise ProviderError("K_AI market fact digits must be an integer") from exc
        if not math.isfinite(digits_numeric) or digits_numeric != digits or not 0 <= digits <= 12:
            raise ProviderError("K_AI market fact digits must be an integer in [0, 12]")

        if bid <= 0 or ask < bid or point <= 0 or tick_value <= 0 or tick_size <= 0 or contract_size <= 0:
            raise ProviderError("K_AI market facts violate positive-price/size invariants")
        if spread < 0 or stop_level < 0 or freeze_level < 0:
            raise ProviderError("K_AI market facts violate non-negative spread/level invariants")

        for field in ("trade_allowed", "terminal_connected", "market_open"):
            if not isinstance(payload[field], bool):
                raise ProviderError(f"K_AI market fact {field} must be boolean")

    @staticmethod
    def _parse_source_time(value: Any, *, field: str) -> datetime:
        text = str(value or "").strip()
        if not text:
            raise ProviderError(f"K_AI {field} is missing")
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ProviderError(f"K_AI {field} must be ISO-8601 compatible") from exc

    @classmethod
    def _validate_scope(cls, scope: str, data: Any) -> None:
        if not isinstance(data, dict) or data.get("timeframe") != scope:
            raise ProviderError(f"Invalid K_AI {scope} scope")
        depth = int(data.get("bar_depth") or 0)
        bars = data.get("bars")
        if depth <= 0 or not isinstance(bars, list) or len(bars) != depth:
            raise ProviderError(f"K_AI {scope} bar depth/count mismatch")

        times: list[datetime] = []
        time_texts: list[str] = []
        for index, bar in enumerate(bars):
            if not isinstance(bar, dict):
                raise ProviderError(f"K_AI {scope} bar {index} is invalid")
            for field in ("time", "open", "high", "low", "close", "volume"):
                if field not in bar:
                    raise ProviderError(f"K_AI {scope} bar {index} missing {field}")

            bar_time_text = str(bar["time"])
            bar_time = cls._parse_source_time(bar_time_text, field=f"{scope} bar {index} time")
            open_ = cls._finite_number(bar["open"], field=f"{scope} bar {index} open")
            high = cls._finite_number(bar["high"], field=f"{scope} bar {index} high")
            low = cls._finite_number(bar["low"], field=f"{scope} bar {index} low")
            close = cls._finite_number(bar["close"], field=f"{scope} bar {index} close")
            volume = cls._finite_number(bar["volume"], field=f"{scope} bar {index} volume")

            if high < low or high < max(open_, close) or low > min(open_, close):
                raise ProviderError(f"K_AI {scope} bar {index} violates OHLC invariants")
            if volume < 0:
                raise ProviderError(f"K_AI {scope} bar {index} volume must be non-negative")

            times.append(bar_time)
            time_texts.append(bar_time_text)

        try:
            ordered = times == sorted(times)
            unique = len(times) == len(set(times))
        except TypeError as exc:
            raise ProviderError(f"K_AI {scope} bar times mix timezone-aware and naive values") from exc
        if not ordered or not unique:
            raise ProviderError(f"K_AI {scope} bars are not strictly chronological")

        latest_text = str(data.get("latest_closed_bar_time") or "")
        if latest_text != time_texts[-1]:
            raise ProviderError(f"K_AI {scope} latest_closed_bar_time mismatch")
        latest = cls._parse_source_time(latest_text, field=f"{scope} latest_closed_bar_time")
        current = cls._parse_source_time(data.get("current_bar_time"), field=f"{scope} current_bar_time")
        try:
            if current <= latest:
                raise ProviderError(
                    f"K_AI {scope} current_bar_time must be after latest_closed_bar_time"
                )
        except TypeError as exc:
            raise ProviderError(
                f"K_AI {scope} current/latest bar times mix timezone-aware and naive values"
            ) from exc

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()
