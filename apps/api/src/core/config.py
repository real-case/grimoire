"""Core configuration using Pydantic BaseSettings."""
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_title: str = Field(default="Grimoire Word Information API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(default="development", description="Environment name")

    # Database
    database_url: str = Field(
        ..., description="PostgreSQL database URL (async format with asyncpg driver)"
    )

    # Redis
    redis_url: str = Field(..., description="Redis connection URL")

    # Anthropic API
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    anthropic_max_tokens: int = Field(default=4096, description="Max tokens for Anthropic API")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022", description="Anthropic model name"
    )

    # Data Sources
    enable_wordnet: bool = Field(default=True, description="Enable WordNet adapter")
    enable_cmu_dict: bool = Field(default=True, description="Enable CMU dictionary adapter")
    enable_cefr_levels: bool = Field(default=True, description="Enable CEFR level adapter")

    # Rate Limiting
    rate_limit_anon_hourly: int = Field(default=100, description="Anonymous hourly rate limit")
    rate_limit_anon_burst: int = Field(default=10, description="Anonymous burst rate limit (per minute)")
    rate_limit_authenticated_hourly: int = Field(
        default=1000, description="Authenticated hourly rate limit"
    )

    # Caching Strategy (TTL in seconds)
    cache_ttl_common_words: int = Field(
        default=0, description="TTL for common words (0 = no expiration)"
    )
    cache_ttl_less_common: int = Field(default=2592000, description="TTL for less common words (30 days)")
    cache_ttl_failed_lookups: int = Field(
        default=3600, description="TTL for failed lookups (1 hour)"
    )

    # Performance
    db_pool_size: int = Field(default=20, description="Database connection pool size")
    db_pool_max_overflow: int = Field(default=10, description="Database pool max overflow")
    redis_pool_min_size: int = Field(default=10, description="Redis pool minimum size")
    redis_pool_max_size: int = Field(default=50, description="Redis pool maximum size")

    # Logging & Monitoring
    sentry_dsn: str = Field(default="", description="Sentry DSN (optional)")
    sentry_traces_sample_rate: float = Field(
        default=0.1, description="Sentry traces sample rate"
    )
    sentry_environment: str = Field(default="development", description="Sentry environment")

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="CORS allow credentials")
    cors_allow_methods: List[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="CORS allowed methods",
    )
    cors_allow_headers: List[str] = Field(default_factory=lambda: ["*"], description="CORS allowed headers")


# Global settings instance
settings = Settings()
