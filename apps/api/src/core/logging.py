"""Logging configuration using loguru with JSON formatting."""
import sys
from typing import Any, Dict

from loguru import logger

from src.core.config import settings


def serialize_log_record(record: Dict[str, Any]) -> str:
    """Serialize log record to JSON format."""
    import json

    log_dict = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add extra fields if present
    if record.get("extra"):
        log_dict.update(record["extra"])

    # Add exception info if present
    if record.get("exception"):
        log_dict["exception"] = {
            "type": record["exception"].type.__name__ if record["exception"].type else None,
            "value": str(record["exception"].value) if record["exception"].value else None,
            "traceback": record["exception"].traceback if record["exception"].traceback else None,
        }

    return json.dumps(log_dict)


def setup_logging() -> None:
    """Configure logging with loguru."""
    # Remove default handler
    logger.remove()

    # Add console handler with JSON formatting for production
    if settings.environment == "production":
        logger.add(
            sys.stdout,
            format=serialize_log_record,
            level=settings.log_level.upper(),
            serialize=True,
        )
    else:
        # Human-readable format for development
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level.upper(),
            colorize=True,
        )

    # Add file handler for errors
    logger.add(
        "logs/error.log",
        rotation="500 MB",
        retention="10 days",
        level="ERROR",
        format=serialize_log_record,
        serialize=True,
    )

    # Initialize Sentry if DSN is provided
    if settings.sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.loguru import LoguruIntegration

            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=settings.sentry_environment,
                traces_sample_rate=settings.sentry_traces_sample_rate,
                integrations=[
                    LoguruIntegration(),
                ],
            )
            logger.info("Sentry integration initialized")
        except ImportError:
            logger.warning("Sentry SDK not installed, skipping Sentry integration")
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")

    logger.info(f"Logging configured with level: {settings.log_level}")
