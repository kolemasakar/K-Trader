from __future__ import annotations

import math

import pytest

from ktrader.providers.base import ProviderError
from ktrader.providers.kai_mt4 import KAIMT4MarketContextAdapter


UNIT_DEPTHS = {"D1": 1, "H1": 1, "M15": 1, "M5": 1}


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
    payload = {
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
    if schema == "1.1":
        payload["timestamp_semantics"] = "BROKER_SERVER_WALL_CLOCK_OPAQUE"
        payload["utc_offset_minutes"] = None
    return payload


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
            _payload("1.0"), require_m15=True
        )


def test_schema_1_1_requires_opaque_timestamp_semantics() -> None:
    payload = _payload("1.1")
    payload.pop("timestamp_semantics")
    with pytest.raises(ProviderError, match="timestamp_semantics"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_schema_1_1_requires_null_utc_offset() -> None:
    payload = _payload("1.1")
    payload["utc_offset_minutes"] = 180
    with pytest.raises(ProviderError, match="utc_offset_minutes must be null"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


@pytest.mark.parametrize("field", ["captured_at", "last_tick_time"])
def test_schema_1_1_rejects_timezone_on_top_level_source_time(field: str) -> None:
    payload = _payload("1.1")
    payload[field] = f"{payload[field]}Z"
    with pytest.raises(ProviderError, match="opaque broker-server wall-clock"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_schema_1_1_rejects_timezone_on_scope_time() -> None:
    payload = _payload("1.1")
    payload["scopes"]["M15"] = _scope(
        "M15", ["2026-09-17T10:00:00+03:00"]
    )
    payload["scopes"]["M15"]["current_bar_time"] = (
        "2026-09-17T10:15:00+03:00"
    )
    with pytest.raises(ProviderError, match="opaque broker-server wall-clock"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_schema_1_1_enforces_expected_m15_depth_when_configured() -> None:
    payload = _payload("1.1")
    expected = dict(UNIT_DEPTHS)
    expected["M15"] = 300
    with pytest.raises(ProviderError, match="M15 bar_depth mismatch"):
        KAIMT4MarketContextAdapter.validate_market_context(
            payload, expected_bar_depths=expected
        )


def test_rejects_missing_snapshot_id() -> None:
    payload = _payload("1.1")
    payload["scopes"]["M15"]["snapshot_id"] = ""
    with pytest.raises(ProviderError, match="missing snapshot_id"):
        KAIMT4MarketContextAdapter.validate_market_context(payload)


def test_rejects_non_chronological_scope() -> None:
    payload = _payload("1.1")
    payload["scopes"]["M15"] = _scope(
        "M15", ["2026-09-17T10:15:00", "2026-09-17T10:00:00"]
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
    [("spread", -1), ("stop_level", -1), ("freeze_level", -1)],
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


def test_accept_market_context_returns_validated_payload() -> None:
    payload = _payload("1.1")
    adapter = KAIMT4MarketContextAdapter(expected_bar_depths=UNIT_DEPTHS)
    result = adapter.accept_market_context(
        payload,
        symbol="USDTRY",
        market="forex",
        require_m15=True,
    )
    assert result is payload


def test_default_accept_rejects_noncanonical_fixture_depths() -> None:
    adapter = KAIMT4MarketContextAdapter()
    with pytest.raises(ProviderError, match="bar_depth mismatch"):
        adapter.accept_market_context(
            _payload("1.1"),
            symbol="USDTRY",
            market="forex",
            require_m15=True,
        )
