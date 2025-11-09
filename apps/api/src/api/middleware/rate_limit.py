"""Rate limiting middleware using slowapi and Redis."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from src.core.config import settings
from src.core.cache import get_redis


def get_redis_for_limiter():
    """Get Redis connection for slowapi limiter."""
    return get_redis()


# Initialize slowapi limiter with Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    default_limits=[],  # We'll set limits per-route
    headers_enabled=True,  # Enable rate limit headers
)


def get_rate_limit_key(request: Request) -> str:
    """
    Generate rate limit key for request.

    Uses IP address for anonymous users.
    In the future, could use API key for authenticated users.

    Args:
        request: FastAPI request object

    Returns:
        Rate limit key string
    """
    # For anonymous users, use IP address
    client_ip = get_remote_address(request)

    # Future: Check for API key authentication
    # api_key = request.headers.get("X-API-Key")
    # if api_key:
    #     return f"user:{api_key}"

    return f"anon:{client_ip}"


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Handle rate limit exceeded exceptions.

    Returns:
        JSONResponse with 429 status and Retry-After header
    """
    # Calculate retry_after from the exception
    retry_after = int(exc.detail.split("Retry after ")[1].split(" seconds")[0]) if "Retry after" in exc.detail else 3600

    response = JSONResponse(
        status_code=429,
        content={
            "error_code": "RATE_LIMIT_EXCEEDED",
            "message": f"You have exceeded the rate limit of {settings.rate_limit_anon_hourly} requests per hour",
            "details": {
                "limit": settings.rate_limit_anon_hourly,
                "window": "1 hour",
                "retry_after": retry_after
            }
        },
        headers={
            "Retry-After": str(retry_after)
        }
    )
    return response


# Rate limit strings for different user types
ANON_HOURLY_LIMIT = f"{settings.rate_limit_anon_hourly}/hour"
ANON_BURST_LIMIT = f"{settings.rate_limit_anon_burst}/minute"
AUTHENTICATED_HOURLY_LIMIT = f"{settings.rate_limit_authenticated_hourly}/hour"


def get_rate_limits() -> list[str]:
    """
    Get rate limit strings for current request.

    Returns:
        List of rate limit strings (e.g., ["100/hour", "10/minute"])
    """
    # For now, return anonymous limits
    # Future: Check authentication and return appropriate limits
    return [ANON_HOURLY_LIMIT, ANON_BURST_LIMIT]
