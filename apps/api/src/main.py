"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from slowapi.errors import RateLimitExceeded

from src.core.config import settings
from src.core.database import init_db, close_db
from src.core.cache import init_redis, close_redis
from src.api.middleware.cors import setup_cors
from src.api.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from src.api.middleware.error_handlers import register_exception_handlers
from src.api.middleware.metrics import PrometheusMiddleware, metrics_endpoint
from src.api.middleware.request_id import RequestIDMiddleware
from src.api.v1.endpoints.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events:
    - Initialize database connection pool
    - Initialize Redis connection
    - Close connections on shutdown
    """
    # Startup
    logger.info("Starting Grimoire API...")

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Initialize Redis
        await init_redis()
        logger.info("Redis initialized")

        logger.info(f"Grimoire API started successfully on {settings.api_host}:{settings.api_port}")

        yield

    finally:
        # Shutdown
        logger.info("Shutting down Grimoire API...")

        # Close database connections
        await close_db()
        logger.info("Database connections closed")

        # Close Redis connections
        await close_redis()
        logger.info("Redis connections closed")

        logger.info("Grimoire API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description="Comprehensive word information API for English as a Foreign Language (EFL) learners. "
                "Provides definitions, phonetics (IPA), usage examples, grammatical information, "
                "synonyms/antonyms, difficulty levels (CEFR), and frequency data.",
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Setup CORS middleware
setup_cors(app)

# Setup request ID middleware (should be early in the chain)
app.add_middleware(RequestIDMiddleware)

# Setup Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

# Setup rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(health_router, prefix="", tags=["system"])

# Word lookup router
from src.api.v1.endpoints.words import router as words_router
app.include_router(words_router, prefix="/api/v1", tags=["words"])

# Prometheus metrics endpoint
app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], tags=["monitoring"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
