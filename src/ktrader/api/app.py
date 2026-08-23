from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

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


def create_app(
    read_model: ApiReadModel | None = None,
    *,
    rate_limit_requests: int = 120,
    rate_limit_window_seconds: int = 60,
    lifespan=None,
) -> FastAPI:
    state = read_model or ApiReadModel()
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
    app.add_middleware(
        FixedWindowRateLimitMiddleware,
        max_requests=rate_limit_requests,
        window_seconds=rate_limit_window_seconds,
    )

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
        return {
            "status": "ok" if status.data_ready and not status.last_error else "degraded",
            "mode": "read_only",
            "api_version": API_VERSION,
            "data_ready": status.data_ready,
            "scanner_status": status.status,
            "provider_id": status.provider_id,
            "generated_at": now.isoformat().replace("+00:00", "Z"),
        }

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
