from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.auth import router as auth_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import urls

app = FastAPI(title="URL Shortener")
app.add_middleware(RateLimitMiddleware)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router.router)
app.include_router(urls.router)