"""CORS middleware configuration."""
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.core.config import settings


def setup_cors(app) -> None:
    """
    Configure CORS middleware for FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    logger.info(f"CORS configured with origins: {settings.cors_origins}")
