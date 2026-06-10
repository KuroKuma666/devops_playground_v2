from fastapi import FastAPI, Query, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from app.core import add, sub


app = FastAPI(title="Test API", version="0.1.0")

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)


@app.middleware("http")
async def count_requests(request: Request, call_next):
    response = await call_next(request)
    http_requests_total.labels(
        request.method,
        request.url.path,
        str(response.status_code),
    ).inc()
    return response


@app.get("/api/health")
def health() -> dict:
    checks = {}
    errors = {}

    try:
        if add(1, 2) != 3:
            raise ValueError("add check returned unexpected result")
    except Exception as exc:
        checks["add"] = "error"
        errors["add"] = str(exc)
    else:
        checks["add"] = "ok"

    try:
        generate_latest()
    except Exception as exc:
        checks["metrics"] = "error"
        errors["metrics"] = str(exc)
    else:
        checks["metrics"] = "ok"

    overall_status = "ok" if not errors else "degraded"

    return {"status": overall_status, "checks": checks, "errors": errors}


@app.get("/api/add")
def add_route(
    x: int = Query(..., description="First integer"),
    y: int = Query(..., description="Second integer"),
) -> dict:
    return {"result": add(x, y)}

@app.get("/api/sub")
def add_route(
    x: int = Query(..., description="First integer"),
    y: int = Query(..., description="Second integer"),
) -> dict:
    return {"result": sub(x, y)}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
