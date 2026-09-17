from __future__ import annotations

import os
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
        if not str(payload.get("run_id") or "").strip():
            raise ProviderError("K_AI market context is missing run_id")
        if not str(payload.get("captured_at") or "").strip():
            raise ProviderError("K_AI market context is missing captured_at")

        scopes = payload.get("scopes")
        if not isinstance(scopes, dict) or set(scopes) != expected_scopes:
            raise ProviderError(
                f"K_AI schema {schema} must contain exactly {sorted(expected_scopes)} scopes"
            )
        for scope in expected_scopes:
            cls._validate_scope(scope, scopes[scope])

    @staticmethod
    def _validate_scope(scope: str, data: Any) -> None:
        if not isinstance(data, dict) or data.get("timeframe") != scope:
            raise ProviderError(f"Invalid K_AI {scope} scope")
        depth = int(data.get("bar_depth") or 0)
        bars = data.get("bars")
        if depth <= 0 or not isinstance(bars, list) or len(bars) != depth:
            raise ProviderError(f"K_AI {scope} bar depth/count mismatch")

        times: list[str] = []
        for index, bar in enumerate(bars):
            if not isinstance(bar, dict):
                raise ProviderError(f"K_AI {scope} bar {index} is invalid")
            for field in ("time", "open", "high", "low", "close", "volume"):
                if field not in bar:
                    raise ProviderError(f"K_AI {scope} bar {index} missing {field}")
            times.append(str(bar["time"]))
        if times != sorted(times) or len(times) != len(set(times)):
            raise ProviderError(f"K_AI {scope} bars are not strictly chronological")
        if str(data.get("latest_closed_bar_time") or "") != times[-1]:
            raise ProviderError(f"K_AI {scope} latest_closed_bar_time mismatch")

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()
