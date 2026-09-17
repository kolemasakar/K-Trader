from __future__ import annotations

from fastapi.testclient import TestClient

from ktrader.api.app import create_app
from ktrader.api.kai_mt4_context import (
    serialize_kai_mt4_candles,
    serialize_kai_mt4_context_summary,
)


def _scope(timeframe: str, count: int) -> dict:
    bars = [
        {
            "time": f"2026-09-17T10:{index:02d}:00",
            "open": 1.0 + index / 1000,
            "high": 1.1 + index / 1000,
            "low": 0.9 + index / 1000,
            "close": 1.05 + index / 1000,
            "volume": 100 + index,
        }
        for index in range(count)
    ]
    return {
        "timeframe": timeframe,
        "snapshot_id": f"snap-{timeframe}",
        "bar_depth": count,
        "latest_closed_bar_time": bars[-1]["time"],
        "current_bar_time": "2026-09-17T11:00:00",
        "bars": bars,
    }


def _payload() -> dict:
    return {
        "schema_version": "1.1",
        "report_type": "MARKET_CONTEXT",
        "run_id": "COMPACT-TEST-1",
        "source_name": "MT4",
        "symbol": "USDTRY",
        "market": "forex",
        "captured_at": "2026-09-17T11:00:01",
        "last_tick_time": "2026-09-17T11:00:00",
        "time_source": "BrokerServer",
        "timestamp_semantics": "BROKER_SERVER_WALL_CLOCK_OPAQUE",
        "utc_offset_minutes": None,
        "closed_bars_only": True,
        "bid": 48.1,
        "ask": 48.2,
        "spread": 100.0,
        "digits": 5,
        "point": 0.00001,
        "tick_value": 0.02,
        "tick_size": 0.00001,
        "contract_size": 100000.0,
        "min_lot": 0.01,
        "max_lot": 100.0,
        "lot_step": 0.01,
        "stop_level": 0.0,
        "freeze_level": 0.0,
        "trade_allowed": True,
        "terminal_connected": True,
        "market_open": True,
        "swap_long": None,
        "swap_short": None,
        "scopes": {
            "D1": _scope("D1", 3),
            "H1": _scope("H1", 3),
            "M15": _scope("M15", 3),
            "M5": _scope("M5", 3),
        },
    }


class StubSource:
    def acquire(self, *, symbol: str, market: str) -> dict:
        assert symbol == "USDTRY"
        assert market == "forex"
        return _payload()


def test_summary_omits_candle_arrays_and_preserves_market_facts() -> None:
    result = serialize_kai_mt4_context_summary(_payload())
    assert result["provider_id"] == "kai_mt4"
    assert result["symbol"] == "USDTRY"
    assert result["swap_long"] is None
    assert result["swap_short"] is None
    assert result["scopes"]["M15"]["bar_depth"] == 3
    assert result["scopes"]["M15"]["bars_available"] == 3
    assert "bars" not in result["scopes"]["M15"]


def test_candle_serializer_returns_bounded_tail() -> None:
    result = serialize_kai_mt4_candles(_payload(), timeframe="m5", limit=2)
    assert result["timeframe"] == "M5"
    assert result["bar_depth"] == 3
    assert result["count"] == 2
    assert len(result["bars"]) == 2
    assert result["bars"] == _payload()["scopes"]["M5"]["bars"][-2:]


def test_summary_action_route_is_compact_and_authenticated() -> None:
    client = TestClient(create_app(action_api_key="secret", kai_mt4_source=StubSource()))
    assert client.get("/v1/mt4/market-context-summary/USDTRY").status_code == 401
    response = client.get(
        "/v1/mt4/market-context-summary/USDTRY",
        params={"market": "forex"},
        headers={"Authorization": "Bearer secret"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider_id"] == "kai_mt4"
    assert payload["scopes"]["D1"]["bars_available"] == 3
    assert "bars" not in payload["scopes"]["D1"]
    assert len(response.content) < 10_000


def test_mt4_candles_action_route_limits_response() -> None:
    client = TestClient(create_app(action_api_key="secret", kai_mt4_source=StubSource()))
    response = client.get(
        "/v1/mt4/candles/USDTRY",
        params={"market": "forex", "timeframe": "M15", "limit": 2},
        headers={"Authorization": "Bearer secret"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["timeframe"] == "M15"
    assert payload["count"] == 2
    assert len(payload["bars"]) == 2


def test_mt4_candles_rejects_invalid_timeframe_and_oversized_limit() -> None:
    client = TestClient(create_app(kai_mt4_source=StubSource()))
    assert client.get(
        "/v1/mt4/candles/USDTRY",
        params={"market": "forex", "timeframe": "H4", "limit": 2},
    ).status_code == 422
    assert client.get(
        "/v1/mt4/candles/USDTRY",
        params={"market": "forex", "timeframe": "M5", "limit": 121},
    ).status_code == 422
