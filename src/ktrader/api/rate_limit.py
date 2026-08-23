from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class FixedWindowRateLimitMiddleware(BaseHTTPMiddleware):
    """Single-process MVP rate limiter.

    Phase 9 may add reverse-proxy enforcement. This middleware intentionally
    does not trust X-Forwarded-For unless deployment adds a trusted-proxy layer.
    """

    def __init__(self, app, *, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        if max_requests <= 0 or window_seconds <= 0:
            raise ValueError("rate-limit values must be positive")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        now = monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            hits = self._hits[client]
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "rate limit exceeded",
                        "retry_after_seconds": self.window_seconds,
                    },
                    headers={"Retry-After": str(self.window_seconds)},
                )
            hits.append(now)
        return await call_next(request)
