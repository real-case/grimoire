"""Prometheus metrics middleware for monitoring API performance."""
import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


# Define Prometheus metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed"
)

cache_hits_total = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["endpoint"]
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total number of cache misses",
    ["endpoint"]
)

word_enrichment_duration_seconds = Histogram(
    "word_enrichment_duration_seconds",
    "Time spent enriching words via external APIs",
    ["source"]
)

error_responses_total = Counter(
    "error_responses_total",
    "Total number of error responses",
    ["endpoint", "error_type"]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for all requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        # Skip metrics collection for the metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        # Track in-progress requests
        http_requests_in_progress.inc()

        # Record start time
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Get endpoint path (without query params)
            endpoint = request.url.path
            method = request.method

            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Track cache hits/misses if header is present
            if "X-Cache-Status" in response.headers:
                cache_status = response.headers["X-Cache-Status"]
                if cache_status == "HIT":
                    cache_hits_total.labels(endpoint=endpoint).inc()
                elif cache_status == "MISS":
                    cache_misses_total.labels(endpoint=endpoint).inc()

            # Track error responses
            if response.status_code >= 400:
                error_type = "client_error" if response.status_code < 500 else "server_error"
                error_responses_total.labels(
                    endpoint=endpoint,
                    error_type=error_type
                ).inc()

            return response

        except Exception as e:
            # Record exception
            duration = time.time() - start_time
            endpoint = request.url.path
            method = request.method

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            error_responses_total.labels(
                endpoint=endpoint,
                error_type="exception"
            ).inc()

            # Re-raise exception
            raise

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.dec()


async def metrics_endpoint(request: Request) -> StarletteResponse:
    """Expose Prometheus metrics at /metrics endpoint."""
    return StarletteResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def record_enrichment_duration(source: str, duration: float) -> None:
    """
    Record the duration of a word enrichment operation.

    Args:
        source: The data source adapter name (e.g., "claude", "wordnet", "cmu")
        duration: Duration in seconds
    """
    word_enrichment_duration_seconds.labels(source=source).observe(duration)
