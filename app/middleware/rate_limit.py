import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

SWEEP_EVERY = 1000   
SWEEP_AGE = 3600     


class RateLimiter:
    """Remembers recent request times per key (like 'general:203.0.113.5')."""

    def __init__(self) -> None:
        self.hits: dict[str, deque[float]] = defaultdict(deque)
        self.checks = 0

    def check(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Return (allowed, seconds_to_wait)."""
        now = time.monotonic()  # a clock that never jumps backwards
        timestamps = self.hits[key]

        while timestamps and timestamps[0] <= now - window:
            timestamps.popleft()

        if len(timestamps) >= limit:
            wait = int(timestamps[0] + window - now) + 1
            return False, wait

        timestamps.append(now)
        self._sweep(now)
        return True, 0

    def _sweep(self, now: float) -> None:
        self.checks += 1
        if self.checks % SWEEP_EVERY:
            return
        stale = [k for k, v in self.hits.items() if not v or v[-1] <= now - SWEEP_AGE]
        for key in stale:
            del self.hits[key]


limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path == "/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        if path == "/auth/login" and request.method == "POST":
            bucket, limit = "login", settings.login_rate_limit_requests
        else:
            bucket, limit = "general", settings.rate_limit_requests

        allowed, retry_after = limiter.check(
            f"{bucket}:{client_ip}", limit, settings.rate_limit_window_seconds
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)