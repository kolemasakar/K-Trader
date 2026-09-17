from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx

from ktrader.providers.base import ProviderError
from ktrader.providers.kai_mt4 import KAIMT4MarketContextAdapter


class KAIMT4ContextUnavailable(RuntimeError):
    pass


class KAIMT4ContextMisconfigured(RuntimeError):
    pass


class KAIMT4MarketContextSource:
    """Read-only client for the bounded K_AI MARKET_CONTEXT delivery surface."""

    def __init__(
        self,
        *,
        auth_token: str,
        uds_path: str | None = None,
        base_url: str = "http://kai-mt4",
        timeout_seconds: float = 70.0,
        adapter: KAIMT4MarketContextAdapter | None = None,
        transport_factory: Callable[[], httpx.BaseTransport] | None = None,
    ) -> None:
        token = auth_token.strip()
        if not token:
            raise ValueError("K_AI delivery auth token is required")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if uds_path is None and transport_factory is None and base_url.startswith("http://kai-mt4"):
            raise ValueError("uds_path is required for the default K_AI base URL")
        self._auth_token = token
        self._uds_path = uds_path
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = float(timeout_seconds)
        self._adapter = adapter or KAIMT4MarketContextAdapter()
        self._transport_factory = transport_factory

    def _transport(self) -> httpx.BaseTransport | None:
        if self._transport_factory is not None:
            return self._transport_factory()
        if self._uds_path:
            return httpx.HTTPTransport(uds=self._uds_path)
        return None

    def acquire(self, *, symbol: str, market: str) -> dict[str, Any]:
        canonical_symbol = symbol.strip()
        canonical_market = market.strip().lower()
        if not canonical_symbol:
            raise ValueError("symbol must be non-empty")
        if not canonical_market:
            raise ValueError("market must be non-empty")

        headers = {"Authorization": f"Bearer {self._auth_token}"}
        transport = self._transport()
        try:
            with httpx.Client(
                base_url=self._base_url,
                transport=transport,
                timeout=self._timeout_seconds,
                headers=headers,
            ) as client:
                response = client.post(
                    "/v1/market-context/acquire",
                    json={"symbol": canonical_symbol, "market": canonical_market},
                )
        except httpx.HTTPError as exc:
            raise KAIMT4ContextUnavailable("K_AI MT4 transport unavailable") from exc

        if response.status_code == 401:
            raise KAIMT4ContextMisconfigured("K_AI MT4 delivery authentication failed")
        if response.status_code in {409, 502, 504}:
            raise KAIMT4ContextUnavailable(
                f"K_AI MT4 context temporarily unavailable ({response.status_code})"
            )
        if response.status_code != 200:
            raise KAIMT4ContextUnavailable(
                f"K_AI MT4 delivery returned HTTP {response.status_code}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise KAIMT4ContextUnavailable("K_AI MT4 delivery returned invalid JSON") from exc

        try:
            return self._adapter.accept_market_context(
                payload,
                symbol=canonical_symbol,
                market=canonical_market,
                require_m15=True,
            )
        except ProviderError as exc:
            raise KAIMT4ContextUnavailable("K_AI MT4 context failed validation") from exc


def serialize_kai_mt4_context(payload: dict[str, Any]) -> dict[str, Any]:
    """Expose an Action-friendly view while preserving canonical source scopes."""

    return {
        "provider_id": "kai_mt4",
        "source_name": payload.get("source_name"),
        "symbol": payload.get("symbol"),
        "market": payload.get("market"),
        "schema_version": payload.get("schema_version"),
        "run_id": payload.get("run_id"),
        "as_of": payload.get("captured_at"),
        "last_tick_time": payload.get("last_tick_time"),
        "time_source": payload.get("time_source"),
        "timestamp_semantics": payload.get("timestamp_semantics"),
        "utc_offset_minutes": payload.get("utc_offset_minutes"),
        "closed_bars_only": payload.get("closed_bars_only"),
        "bid": payload.get("bid"),
        "ask": payload.get("ask"),
        "spread": payload.get("spread"),
        "digits": payload.get("digits"),
        "point": payload.get("point"),
        "tick_value": payload.get("tick_value"),
        "tick_size": payload.get("tick_size"),
        "contract_size": payload.get("contract_size"),
        "min_lot": payload.get("min_lot"),
        "max_lot": payload.get("max_lot"),
        "lot_step": payload.get("lot_step"),
        "stop_level": payload.get("stop_level"),
        "freeze_level": payload.get("freeze_level"),
        "trade_allowed": payload.get("trade_allowed"),
        "terminal_connected": payload.get("terminal_connected"),
        "market_open": payload.get("market_open"),
        "swap_long": payload.get("swap_long"),
        "swap_short": payload.get("swap_short"),
        "scopes": payload.get("scopes"),
    }
