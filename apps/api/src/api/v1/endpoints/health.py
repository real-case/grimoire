"""Health check endpoint."""
from datetime import datetime

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database import get_db
from src.core.cache import get_redis_dependency

router = APIRouter(tags=["system"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dependency)
):
    """
    Health check endpoint.

    Checks connectivity to:
    - Database (PostgreSQL)
    - Cache (Redis)

    Returns:
        Health status with service availability
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {}
    }

    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "up"
        logger.debug("Database health check: OK")
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["database"] = "down"
        logger.error(f"Database health check failed: {e}")

    # Check Redis connectivity
    try:
        await redis.ping()
        health_status["services"]["cache"] = "up"
        logger.debug("Redis health check: OK")
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["cache"] = "down"
        logger.error(f"Redis health check failed: {e}")

    # Future: Add AI service check
    # For now, we'll just mark it as up
    health_status["services"]["ai_service"] = "up"

    return health_status
