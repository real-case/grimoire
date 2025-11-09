"""Pytest configuration and shared fixtures for all tests."""
import os
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up environment variables for all tests (runs once per session)."""
    # Set required environment variables before any imports
    test_env = {
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/0",
        "ANTHROPIC_API_KEY": "test-api-key-12345",
        "ANTHROPIC_MAX_TOKENS": "4096",
        "ANTHROPIC_MODEL": "claude-3-5-sonnet-20241022",
        "API_HOST": "0.0.0.0",
        "API_PORT": "8000",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "INFO",
    }

    # Store original values to restore later
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield

    # Restore original environment variables
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture(autouse=True)
def mock_anthropic_client(monkeypatch):
    """Mock the Anthropic client to prevent actual API calls during tests."""
    mock_client = MagicMock()

    # Mock the AsyncAnthropic class
    with patch("src.services.claude_enrichment_adapter.AsyncAnthropic") as mock_anthropic:
        mock_anthropic.return_value = mock_client
        yield mock_client


@pytest.fixture(autouse=True)
def mock_logger(monkeypatch):
    """Mock loguru logger to reduce test output noise."""
    with patch("src.services.enrichment_service.logger"):
        with patch("src.services.claude_enrichment_adapter.logger"):
            yield
