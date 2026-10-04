from fastapi import FastAPI

from app.routers import urls

app = FastAPI(title="URL Shortener")


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Included AFTER /health on purpose: the redirect route /{slug} matches almost
# any path, so specific routes must be registered first.
app.include_router(urls.router)