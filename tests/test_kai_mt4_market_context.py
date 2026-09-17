from __future__ import annotations

import math

import httpx
import pytest

from ktrader.providers.base import ProviderError
from ktrader.providers.kai_mt4 import KAIMT4MarketContextAdapter


def _scope(name: str, times: list[str] | None = None) -> dict:
    times = times or ["2026-09-17T10:00:00"]
    bars = [
        {
            "time": value,
            "open": 1.0,
            "high": 1.2,
            "low": 0.9,
            "close": 1.1,
            "volume": 10,
        }
        for value in times
    ]
    return {
        "timeframe": name,
        "snapshot_id": f"snap-{name}",
        "bar_depth": len(bars),
        "latest_closed_bar_time": bars[-1]["time"],
        "current_bar_time": "2026-09-17T10:15:00",
        "bars": bars,
    }


def _payload(schema: str = "1.1") -> dict:
    scopes = {"D1": _scope("D1"), "H1": _scope("H1"), "M5": _scope("M5")}
    if schema == "1.1":
        scopes["M15"] = _scope("M15")
    return {
        "schema_version": schema,
        "report_type": "MARKET_CONTEXT",
        "run_id": "KTRADER-TEST-1",
        "source_name": "MT4",
        "symbol": "USDTRY",
        "market": "forex",
        "captured_at": "2026-09-17T10:15:01",
        "last_tick_time": "2026-09-17T10:15:00",
        "time_source": "BrokerServer",
        "bid": 41.10,
        "ask": 41.11,
        "spread": 10.0,
        "digits": 3,
        "point": 0.001,
        "stop_level": 0,
        "freeze_level": 0,
        "tick_value": 1.0,
        "tick_size": 0.001,
        "contract_size": 100000.0,
        "trade_allowed": True,
        "terminal_connected": True,
        "market_open": True,
        "data_quality_flag": "VALID",
        "closed_bars_only": True,
        "scopes": scopes,
    }


def test_schema_1_1_accepts_native_m15() -> None:
    KAIMT4MarketContextAdapter.validate_market_context(
        _payload("1.1"),
        expected_symbol="USDTRY",
        expected_market="forex",
        require_m15=True,
    )


def test_schema_1_0_is_backward_compatible_without_m15_requirement() -> None:
    KAIMT4MarketContextAdapter.validate_market_context(
        _payload("1.0"),
        expected_symbol="USDTRY",
        expected_market="forex",
    )


def test_schema_1_0_fails_when_m15_is_required() -> None:
    with pytest.raises(ProviderError, match="M15 requires"):
        KAIMT4MarketContextAdapter.validate_market_context(
            _payload("1.0"),
            require_m15=True,
        )


def test_rejects_non_chronological_scope() -> None:
    payload = _payload("1.1")
    payload["scopes"]["M15"] = _scope(
        "M15",
        ["2026-09-17T10:15:00", "2026-09-17T10:00:00"],
    )
    with pytest.raises(ProviderError, match="strictly chronological"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_rejects_invalid_market_facts() -> None:
    payload = _payload("1.1")
    payload["ask"] = 40.0
    with pytest.raises(ProviderError, match="positive-price/size invariants"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("spread", -1),
        ("stop_level", -1),
        ("freeze_level", -1),
    ],
)
def test_rejects_negative_market_levels(field: str, value: float) -> None:
    payload = _payload("1.1")
    payload[field] = value
    with pytest.raises(ProviderError, match="non-negative spread/level invariants"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


@pytest.mark.parametrize("value", [3.5, -1, 13, True])
def test_rejects_invalid_digits(value: object) -> None:
    payload = _payload("1.1")
    payload["digits"] = value
    with pytest.raises(ProviderError, match="digits must be"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_rejects_non_finite_market_fact() -> None:
    payload = _payload("1.1")
    payload["spread"] = math.inf
    with pytest.raises(ProviderError, match="must be finite"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_rejects_ohlc_invariant_violation() -> None:
    payload = _payload("1.1")
    payload["scopes"]["M15"]["bars"][0]["high"] = 1.05
    with pytest.raises(ProviderError, match="OHLC invariants"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_rejects_negative_volume() -> None:
    payload = _payload("1.1")
    payload["scopes"]["M15"]["bars"][0]["volume"] = -1
    with pytest.raises(ProviderError, match="volume must be non-negative"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_rejects_non_finite_bar_value() -> None:
    payload = _payload("1.1")
    payload["scopes"]["M15"]["bars"][0]["close"] = math.nan
    with pytest.raises(ProviderError, match="must be finite"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_rejects_current_bar_not_after_latest_closed_bar() -> None:
    payload = _payload("1.1")
    payload["scopes"]["M15"]["current_bar_time"] = payload["scopes"]["M15"][
        "latest_closed_bar_time"
    ]
    with pytest.raises(ProviderError, match="current_bar_time must be after"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_rejects_invalid_bar_timestamp() -> None:
    payload = _payload("1.1")
    payload["scopes"]["M15"]["bars"][0]["time"] = "not-a-time"
    payload["scopes"]["M15"]["latest_closed_bar_time"] = "not-a-time"
    with pytest.raises(ProviderError, match="ISO-8601 compatible"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


@pytest.mark.asyncio
async def test_acquire_posts_only_symbol_and_market_and_validates_response() -> None:
    payload = _payload("1.1")

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/market-context/acquire"
        assert request.content == b'{"symbol":"USDTRY","market":"forex"}'
        return httpx.Response(200, json=payload)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = KAIMT4MarketContextAdapter(
        base_url="http://127.0.0.1:8765",
        client=client,
    )
    try:
        result = await adapter.acquire_market_context(
            "USDTRY",
            "forex",
            require_m15=True,
        )
    finally:
        await client.aclose()

    assert result == payload


@pytest.mark.asyncio
async def test_http_failure_is_provider_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"detail": "bridge unavailable"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = KAIMT4MarketContextAdapter(base_url="http://127.0.0.1:8765", client=client)
    try:
        with pytest.raises(ProviderError, match="request failed"):
            await adapter.acquire_market_context("USDTRY", "forex")
    finally:
        await client.aclose()
