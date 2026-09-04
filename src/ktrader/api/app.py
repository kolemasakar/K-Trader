from __future__ import annotations

from datetime import datetime, timezone
import hmac

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from ktrader.api.rate_limit import FixedWindowRateLimitMiddleware
from ktrader.api.serialization import (
    serialize_candle_series,
    serialize_decision,
    serialize_status,
    serialize_universe_candidate,
)
from ktrader.api.state import (
    AmbiguousSymbolError,
    ApiReadModel,
    SymbolNotFoundError,
)


API_VERSION = "phase8-v1"
ALLOWED_INTERVALS = {"5m", "15m", "1h", "4h", "1d"}
ALLOWED_GRADES = {"A+", "A", "B", "C"}
PRIVACY_POLICY_TEXT = """K-Trader Action Privacy Policy

K-Trader exposes read-only public derivatives market data and deterministic scanner results to the K_Trader Custom GPT. It does not accept exchange credentials, does not access exchange accounts, and cannot place, modify, or cancel orders.

The API is designed not to store ChatGPT prompts or conversation content. Normal infrastructure and application logs may contain technical request metadata such as timestamp, client/network address, HTTP path, status code, and diagnostic information needed to operate and secure the service.

Market-data requests may be forwarded to configured public exchange market-data endpoints. No ChatGPT account credentials or exchange account credentials are sent to those providers.

Contact and policy-owner details should be added before public GPT distribution if required by the selected publishing mode.
"""


def create_app(
    read_model: ApiReadModel | None = None,
    *,
    rate_limit_requests: int = 120,
    rate_limit_window_seconds: int = 60,
    lifespan=None,
    action_api_key: str | None = None,
    health_max_scan_age_seconds: float | None = None,
) -> FastAPI:
    state = read_model or ApiReadModel()
    secret = action_api_key.strip() if action_api_key and action_api_key.strip() else None
    if health_max_scan_age_seconds is not None and health_max_scan_age_seconds <= 0:
        raise ValueError("health_max_scan_age_seconds must be positive when configured")
    app = FastAPI(
        title="K-Trader Read-only API",
        version=API_VERSION,
        description=(
            "Read-only market scanner API for K_Trader. "
            "No order, account or exchange-credential endpoints exist in v1."
        ),
        lifespan=lifespan,
    )
    app.state.read_model = state
    app.state.action_auth_enabled = secret is not None
    app.state.health_max_scan_age_seconds = health_max_scan_age_seconds
    app.add_middleware(
        FixedWindowRateLimitMiddleware,
        max_requests=rate_limit_requests,
        window_seconds=rate_limit_window_seconds,
    )

    @app.middleware("http")
    async def action_auth(request: Request, call_next):
        if secret is not None and request.url.path.startswith("/v1/"):
            authorization = request.headers.get("authorization", "")
            prefix = "Bearer "
            supplied = authorization[len(prefix):] if authorization.startswith(prefix) else ""
            if not supplied or not hmac.compare_digest(supplied, secret):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "unauthorized"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return await call_next(request)

    @app.exception_handler(SymbolNotFoundError)
    async def not_found_handler(_request: Request, exc: SymbolNotFoundError):
        return JSONResponse(status_code=404, content={"detail": f"symbol not found: {exc}"})

    @app.exception_handler(AmbiguousSymbolError)
    async def ambiguous_handler(_request: Request, exc: AmbiguousSymbolError):
        return JSONResponse(
            status_code=409,
            content={
                "detail": str(exc),
                "resolution": "repeat the request with provider_id",
            },
        )

    @app.get("/health", operation_id="getHealth")
    def health() -> dict:
        status = state.get_status()
        now = datetime.now(timezone.utc)
        watchdog_ok = True
        if health_max_scan_age_seconds is not None:
            if status.last_scan_at is None:
                watchdog_ok = False
            else:
                age = max(0.0, (now - status.last_scan_at.astimezone(timezone.utc)).total_seconds())
                watchdog_ok = age <= health_max_scan_age_seconds
        return {
            "status": "ok" if status.data_ready and watchdog_ok else "degraded",
            "mode": "read_only",
            "api_version": API_VERSION,
            "data_ready": status.data_ready,
            "scanner_status": status.status,
            "provider_id": status.provider_id,
            "action_auth_enabled": secret is not None,
            "generated_at": now.isoformat().replace("+00:00", "Z"),
        }

    @app.get("/privacy", include_in_schema=False)
    def privacy_policy():
        return PlainTextResponse(PRIVACY_POLICY_TEXT)

    @app.get("/v1/scanner/status", operation_id="getScannerStatus")
    def scanner_status() -> dict:
        return serialize_status(state.get_status(), started_at=state.started_at)

    @app.get("/v1/universe", operation_id="listUniverse")
    def universe(
        provider_id: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=200),
    ) -> dict:
        now = datetime.now(timezone.utc)
        items = state.list_universe(provider_id=provider_id)[:limit]
        return {
            "count": len(items),
            "provider_id": provider_id,
            "items": [serialize_universe_candidate(item, now=now) for item in items],
        }

    @app.get("/v1/market/{symbol}", operation_id="getMarketSnapshot")
    def market_snapshot(
        symbol: str,
        provider_id: str | None = Query(default=None),
    ) -> dict:
        now = datetime.now(timezone.utc)
        return serialize_universe_candidate(
            state.resolve_market(symbol, provider_id=provider_id),
            now=now,
        )

    @app.get("/v1/candles/{symbol}", operation_id="getCandles")
    def candles(
        symbol: str,
        provider_id: str | None = Query(default=None),
        interval: str = Query(default="5m"),
        limit: int = Query(default=100, ge=1, le=500),
    ) -> dict:
        if interval not in ALLOWED_INTERVALS:
            raise HTTPException(
                status_code=422,
                detail=f"interval must be one of {sorted(ALLOWED_INTERVALS)}",
            )
        series = state.resolve_candles(
            symbol,
            interval=interval,
            provider_id=provider_id,
        )
        return serialize_candle_series(series, limit=limit)

    @app.get("/v1/analysis/{symbol}", operation_id="getAnalysis")
    def analysis(
        symbol: str,
        provider_id: str | None = Query(default=None),
    ) -> dict:
        return serialize_decision(
            state.resolve_analysis(symbol, provider_id=provider_id)
        )

    @app.get("/v1/candidates", operation_id="listCandidates")
    def candidates(
        provider_id: str | None = Query(default=None),
        grade: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=200),
    ) -> dict:
        if grade is not None and grade not in ALLOWED_GRADES:
            raise HTTPException(
                status_code=422,
                detail=f"grade must be one of {sorted(ALLOWED_GRADES)}",
            )
        items = state.list_candidates(provider_id=provider_id, grade=grade)[:limit]
        return {
            "count": len(items),
            "items": [serialize_decision(item) for item in items],
        }

    @app.get("/v1/signals", operation_id="listSignals")
    def signals(
        provider_id: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=200),
    ) -> dict:
        items = state.list_signals(provider_id=provider_id)[:limit]
        return {
            "count": len(items),
            "items": [serialize_decision(item) for item in items],
        }

    return app


app = create_app()
