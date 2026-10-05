from fastapi import FastAPI

from app.auth import router as auth_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import urls

app = FastAPI(title="URL Shortener")

# Every request now passes through the rate limiter first.
app.add_middleware(RateLimitMiddleware)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Order matters: urls.router contains the catch-all /{slug}, so it goes last.
app.include_router(auth_router.router)
app.include_router(urls.router)