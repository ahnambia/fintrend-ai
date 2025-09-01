from fastapi import FastAPI
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from api.routes import sentiment as sentiment_routes

app = FastAPI(title="FinTrend AI API")
app.include_router(sentiment_routes.router, prefix="/sentiment", tags=["sentiment"])

# Example metric
REQUEST_COUNT = Counter("request_count", "Total number of requests")

@app.get("/health")
def health():
    REQUEST_COUNT.inc()
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
