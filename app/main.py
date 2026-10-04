from fastapi import FastAPI
app=FastAPI(title="URL Shortener")

@app.get("/health")
def health_check():
    return {"status": "ok"}
