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


def _base_action_fields(payload: dict[str, Any]) -> dict[str, Any]:
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
    }


def serialize_kai_mt4_context(payload: dict[str, Any]) -> dict[str, Any]:
    """Expose the full validated context for backend/E2E use."""

    return {
        **_base_action_fields(payload),
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


def serialize_kai_mt4_context_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Compact Action-safe context metadata without candle arrays."""

    scopes = payload.get("scopes") or {}
    scope_summary: dict[str, dict[str, Any]] = {}
    for timeframe in ("D1", "H1", "M15", "M5"):
        scope = scopes.get(timeframe) or {}
        scope_summary[timeframe] = {
            "timeframe": scope.get("timeframe"),
            "snapshot_id": scope.get("snapshot_id"),
            "bar_depth": scope.get("bar_depth"),
            "latest_closed_bar_time": scope.get("latest_closed_bar_time"),
            "current_bar_time": scope.get("current_bar_time"),
            "bars_available": len(scope.get("bars") or ()),
        }

    return {
        **_base_action_fields(payload),
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
        "scopes": scope_summary,
    }


def serialize_kai_mt4_candles(
    payload: dict[str, Any],
    *,
    timeframe: str,
    limit: int,
) -> dict[str, Any]:
    """Return a bounded tail of one validated MT4 timeframe for ChatGPT Actions."""

    canonical_timeframe = timeframe.strip().upper()
    scopes = payload.get("scopes") or {}
    if canonical_timeframe not in {"D1", "H1", "M15", "M5"}:
        raise ValueError("timeframe must be one of D1, H1, M15, M5")
    if limit < 1 or limit > 120:
        raise ValueError("limit must be between 1 and 120")
    scope = scopes.get(canonical_timeframe)
    if not isinstance(scope, dict):
        raise ValueError(f"timeframe {canonical_timeframe} is unavailable")
    bars = list(scope.get("bars") or ())
    selected = bars[-limit:]
    return {
        **_base_action_fields(payload),
        "timeframe": canonical_timeframe,
        "snapshot_id": scope.get("snapshot_id"),
        "bar_depth": scope.get("bar_depth"),
        "latest_closed_bar_time": scope.get("latest_closed_bar_time"),
        "current_bar_time": scope.get("current_bar_time"),
        "count": len(selected),
        "bars": selected,
    }
