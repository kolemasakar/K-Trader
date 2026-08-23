from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from ktrader.api import ApiReadModel, ScannerRuntimeStatus, create_app
from ktrader.engine.models import TradingDecision
from ktrader.market.universe import UniverseCandidate
from ktrader.models import NormalizedCandle, NormalizedInstrument, NormalizedTicker


UTC = timezone.utc
NOW = datetime(2026, 8, 23, 10, 0, tzinfo=UTC)


def instrument(provider: str, symbol: str = "SUIUSDT") -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id=provider,
        symbol=symbol,
        provider_symbol=symbol,
        base_asset="SUI",
        quote_asset="USDT",
        market_type="linear_perpetual",
        contract_type="PERPETUAL",
        status="TRADING",
        price_tick=Decimal("0.0001"),
        quantity_step=Decimal("0.1"),
    )


def universe_candidate(provider: str, symbol: str = "SUIUSDT") -> UniverseCandidate:
    item = instrument(provider, symbol)
    ticker = NormalizedTicker(
        provider_id=provider,
        symbol=symbol,
        timestamp=NOW,
        last_price=Decimal("0.742100"),
        quote_volume_24h=Decimal("1234567.890123"),
        base_volume_24h=Decimal("1663600"),
        bid_price=Decimal("0.7420"),
        ask_price=Decimal("0.7422"),
    )
    return UniverseCandidate(item, ticker, Decimal("987654.321"))


def candle(provider: str, minute: int, *, interval: str = "5m") -> NormalizedCandle:
    open_time = NOW + timedelta(minutes=minute)
    return NormalizedCandle(
        provider_id=provider,
        symbol="SUIUSDT",
        interval=interval,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=5) - timedelta(milliseconds=1),
        open=Decimal("0.7400"),
        high=Decimal("0.7450"),
        low=Decimal("0.7390"),
        close=Decimal("0.7420"),
        volume=Decimal("100000.25"),
        quote_volume=Decimal("74200.125"),
        closed=True,
    )


def decision(provider: str, *, side: str = "LONG", grade: str = "A") -> TradingDecision:
    return TradingDecision(
        provider_id=provider,
        exchange=provider,
        canonical_symbol="SUIUSDT",
        provider_symbol="SUIUSDT",
        market_type="linear_perpetual",
        side=side,
        grade=grade,
        setup_score=84 if grade == "A" else 65,
        raw_score=84 if grade == "A" else 65,
        setup_type="TRAP_VSA_CONFIRMATION",
        market_regime="BULLISH",
        trend_context="BULLISH",
        liquidity_rank=3,
        liquidity_score=Decimal("987654.321"),
        sessions=("LONDON", "NEW_YORK"),
        session_overlap=True,
        strength="STRONG",
        primary_level_id="level-1",
        primary_level_strength="STRONG",
        trap_state="CONFIRMED",
        vsa_events=("NS",),
        entry=Decimal("0.7422") if side != "NO_TRADE" else None,
        luft=Decimal("0.0002") if side != "NO_TRADE" else None,
        stop=Decimal("0.7350") if side != "NO_TRADE" else None,
        target=Decimal("0.7640") if side != "NO_TRADE" else None,
        rr=Decimal("3.0277777778"),
        atr5d=Decimal("0.041"),
        atr_used_pct=Decimal("36.25"),
        atr_state="STRONG",
        position_size=None,
        risk_amount=None,
        risk_percent=None,
        reason_codes=() if side != "NO_TRADE" else ("GRADE_BELOW_A",),
        data_time=NOW,
        last_closed_bar=NOW - timedelta(seconds=1),
        data_age_seconds=1.0,
        freshness_status="FRESH",
        generated_at=NOW,
    )


def ready_state() -> ApiReadModel:
    state = ApiReadModel()
    state.set_status(
        ScannerRuntimeStatus(
            status="RUNNING",
            provider_id="binance_usdm",
            universe_size=1,
            data_ready=True,
            last_scan_at=NOW,
        )
    )
    state.replace_universe([universe_candidate("binance_usdm")])
    state.put_candles(
        provider_id="binance_usdm",
        symbol="SUIUSDT",
        interval="5m",
        candles=[candle("binance_usdm", 0), candle("binance_usdm", 5)],
        source_kind="provider",
    )
    state.replace_decisions([decision("binance_usdm")])
    return state


def test_health_and_read_only_openapi():
    client = TestClient(create_app(ready_state()))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "read_only"
    assert response.json()["status"] == "ok"

    schema = client.get("/openapi.json").json()
    for path, operations in schema["paths"].items():
        assert set(operations).issubset({"get", "parameters"}), path


def test_market_precision_is_serialized_as_decimal_strings():
    client = TestClient(create_app(ready_state()))
    payload = client.get(
        "/v1/market/SUIUSDT",
        params={"provider_id": "binance_usdm"},
    ).json()
    assert payload["last_price"] == "0.742100"
    assert payload["quote_volume_24h"] == "1234567.890123"
    assert payload["price_tick"] == "0.0001"


def test_symbol_ambiguity_requires_provider_id():
    state = ready_state()
    state.replace_universe(
        [
            universe_candidate("binance_usdm"),
            universe_candidate("bybit_linear"),
        ]
    )
    client = TestClient(create_app(state))
    response = client.get("/v1/market/SUIUSDT")
    assert response.status_code == 409
    assert response.json()["resolution"] == "repeat the request with provider_id"
    assert client.get(
        "/v1/market/SUIUSDT",
        params={"provider_id": "bybit_linear"},
    ).status_code == 200


def test_candles_tail_and_source_kind():
    client = TestClient(create_app(ready_state()))
    payload = client.get(
        "/v1/candles/SUIUSDT",
        params={"provider_id": "binance_usdm", "interval": "5m", "limit": 1},
    ).json()
    assert payload["count"] == 1
    assert payload["source_kind"] == "provider"
    assert payload["candles"][0]["close"] == "0.7420"


def test_analysis_candidates_and_signal_filter():
    state = ready_state()
    no_trade = decision("binance_usdm", side="NO_TRADE", grade="C")
    state.replace_decisions([decision("binance_usdm"), no_trade])
    client = TestClient(create_app(state))

    analysis = client.get(
        "/v1/analysis/SUIUSDT",
        params={"provider_id": "binance_usdm"},
    ).json()
    assert analysis["side"] == "LONG"
    assert analysis["estimated_probability"] is None

    candidates = client.get("/v1/candidates").json()
    signals = client.get("/v1/signals").json()
    assert candidates["count"] == 2
    assert signals["count"] == 1
    assert signals["items"][0]["side"] == "LONG"


def test_invalid_interval_fails_closed():
    client = TestClient(create_app(ready_state()))
    response = client.get(
        "/v1/candles/SUIUSDT",
        params={"provider_id": "binance_usdm", "interval": "3m"},
    )
    assert response.status_code == 422


def test_rate_limit_returns_429():
    client = TestClient(
        create_app(
            ready_state(),
            rate_limit_requests=1,
            rate_limit_window_seconds=60,
        )
    )
    assert client.get("/health").status_code == 200
    response = client.get("/health")
    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"
