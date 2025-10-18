"""Global error handling middleware for FastAPI."""
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from src.api.v1.models.responses import ErrorResponse
from src.api.middleware.request_id import get_request_id


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request
        exc: Validation exception

    Returns:
        JSONResponse with 400 status
    """
    errors = exc.errors()
    request_id = get_request_id(request)
    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "request_id": request_id,
            "details": {
                "errors": errors
            }
        }
    )


async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.

    Args:
        request: FastAPI request
        exc: Database exception

    Returns:
        JSONResponse with 500 status
    """
    request_id = get_request_id(request)
    logger.error(f"Database error on {request.url.path}: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "DATABASE_ERROR",
            "message": "A database error occurred. Please try again later.",
            "request_id": request_id,
            "details": {}
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle all other unexpected exceptions.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSONResponse with 500 status
    """
    request_id = get_request_id(request)
    logger.error(f"Unexpected error on {request.url.path}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request_id,
            "details": {
                "type": type(exc).__name__
            }
        }
    )


class WordNotFoundException(Exception):
    """Exception raised when a word is not found."""

    def __init__(self, word: str, suggestions: list[str] = None):
        self.word = word
        self.suggestions = suggestions or []
        super().__init__(f"Word '{word}' not found")


async def word_not_found_handler(
    request: Request,
    exc: WordNotFoundException
) -> JSONResponse:
    """
    Handle word not found exceptions with spelling suggestions (T072).

    Args:
        request: FastAPI request
        exc: WordNotFoundException

    Returns:
        JSONResponse with 404 status and spelling suggestions
    """
    request_id = get_request_id(request)
    logger.info(f"Word not found: {exc.word}")

    # Format suggestions as "Did you mean: 'word'?"
    formatted_suggestions = [f"Did you mean: '{suggestion}'?" for suggestion in exc.suggestions]

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error_code": "WORD_NOT_FOUND",
            "message": f"The word '{exc.word}' was not found in our database",
            "request_id": request_id,
            "suggestions": formatted_suggestions
        }
    )


class InvalidWordFormatException(Exception):
    """Exception raised when word format is invalid."""

    def __init__(self, word: str, pattern: str = "^[a-zA-Z]+(-[a-zA-Z]+)*$"):
        self.word = word
        self.pattern = pattern
        super().__init__(f"Invalid word format: '{word}'")


async def invalid_word_format_handler(
    request: Request,
    exc: InvalidWordFormatException
) -> JSONResponse:
    """
    Handle invalid word format exceptions.

    Args:
        request: FastAPI request
        exc: InvalidWordFormatException

    Returns:
        JSONResponse with 400 status
    """
    request_id = get_request_id(request)
    logger.warning(f"Invalid word format: {exc.word}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "INVALID_WORD_FORMAT",
            "message": "Word must contain only letters and hyphens",
            "request_id": request_id,
            "details": {
                "field": "word",
                "pattern": exc.pattern,
                "provided": exc.word
            }
        }
    )


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(WordNotFoundException, word_not_found_handler)
    app.add_exception_handler(InvalidWordFormatException, invalid_word_format_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered")
