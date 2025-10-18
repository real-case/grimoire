"""Request ID tracing middleware."""
import uuid
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request IDs for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add a unique request ID to each request.

        The request ID is:
        1. Taken from X-Request-ID header if provided
        2. Generated as a new UUID if not provided
        3. Added to the response headers
        4. Added to log context for all logs during request processing
        """
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Add request ID to request state for access in route handlers
        request.state.request_id = request_id

        # Add request ID to log context
        with logger.contextualize(request_id=request_id):
            logger.info(
                f"Request started: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client_host": request.client.host if request.client else None,
                }
            )

            try:
                # Process request
                response = await call_next(request)

                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id

                logger.info(
                    f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                    }
                )

                return response

            except Exception as e:
                logger.error(
                    f"Request failed: {request.method} {request.url.path} - {str(e)}",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                    }
                )
                raise


def get_request_id(request: Request) -> str:
    """
    Get the request ID from the current request.

    Args:
        request: The FastAPI request object

    Returns:
        The request ID as a string
    """
    return getattr(request.state, "request_id", "unknown")
