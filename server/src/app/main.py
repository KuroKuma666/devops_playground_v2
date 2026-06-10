from fastapi import FastAPI, Query, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from app.core import add, sub

# Create a FastAPI backend
app = FastAPI(title="Test API", version="0.1.0")

# Defining a Prometheus counter to track HTTP requests:
# - `http_requests_total`: The name of the metric.
# - "Total HTTP requests": A description of the metric.
# - `["method", "path", "status"]`: The labels for the metric, which will allow us to track requests by HTTP method, path, and response status code. e.g. http_requests_total{method="GET", path="/api/health", status="200"} 5
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

# Middleware to count HTTP requests. The middleware runs on every incoming HTTP request, and it uses the `http_requests_total` counter to increment the count for each request based on its method, path, and response status code. We need the middleware because otherwiese the app would expose Prometheus, but it would not count the requests automatically. The middleware allows us to hook into the request processing pipeline and update our metrics accordingly - it records the traffic.
@app.middleware("http")
async def count_requests(request: Request, call_next):
    # Call the next middleware or route handler with `call_next(request)`, which processes the request and returns a response. After receiving the response, we can access its status code to update our Prometheus counter.
    response: Response = await call_next(request)
    # Increment the Prometheus counter with the appropriate labels for method, path, and status code.
    http_requests_total.labels(
        request.method,
        request.url.path,
        str(response.status_code),
    ).inc()
    # Return the response to the client.
    return response


@app.get("/api/health")
def health() -> dict:
    checks = {}
    errors = {}

    try:
        if add(1, 2) != 3:
            raise ValueError("add check returned unexpected result")
        if sub(5, 3) != 2:
            raise ValueError("sub check returned unexpected result")
    except Exception as exc:
        checks["add"] = "error"
        errors["add"] = str(exc)
        checks["sub"] = "error"
        errors["sub"] = str(exc)
    else:
        checks["add"] = "ok"
        checks["sub"] = "ok"

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
def sub_route(
    x: int = Query(..., description="First integer"),
    y: int = Query(..., description="Second integer"),
) -> dict:
    return {"result": sub(x, y)}

# This is the endpoint that Prometheus will scrape to collect metrics. When Prometheus scrapes this endpoint, it will receive the latest metrics in a format that it can understand and process. The `generate_latest()` function from the `prometheus_client` library is used to generate the latest metrics data, and we set the `Content-Type` header to `CONTENT_TYPE_LATEST` to indicate that the response contains Prometheus metrics. So, when Prometheus calls http://server:8000/metrics, it receives data like request counters, process metrics, and any custom metrics we have defined, which it can then store and use for monitoring and alerting purposes.
@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
