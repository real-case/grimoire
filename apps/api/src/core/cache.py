"""Redis connection and cache utilities."""
from typing import Optional, Any
import json

from redis.asyncio import Redis, ConnectionPool
from loguru import logger

from src.core.config import settings


# Redis connection pool
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None


def get_redis_pool() -> ConnectionPool:
    """Get or create Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=settings.redis_pool_max_size,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )
    return _redis_pool


def get_redis() -> Redis:
    """Get Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(connection_pool=get_redis_pool())
    return _redis_client


async def get_redis_dependency() -> Redis:
    """
    Dependency for getting Redis client in FastAPI.

    Usage:
        @app.get("/endpoint")
        async def endpoint(redis: Redis = Depends(get_redis_dependency)):
            ...
    """
    return get_redis()


def build_cache_key(prefix: str, identifier: str) -> str:
    """
    Build cache key with namespace prefix.

    Args:
        prefix: Cache key prefix (e.g., "word", "definition")
        identifier: Unique identifier (e.g., word text)

    Returns:
        Formatted cache key (e.g., "grimoire:word:serendipity")
    """
    return f"grimoire:{prefix}:{identifier}"


async def init_redis() -> None:
    """Initialize Redis connection."""
    try:
        redis = get_redis()
        await redis.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client, _redis_pool
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None
    logger.info("Redis connection closed")


class CacheService:
    """Service for caching word data with TTL strategy."""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_cached_word(self, word: str) -> Optional[dict[str, Any]]:
        """
        Get cached word data.

        Args:
            word: Word text (normalized)

        Returns:
            Cached word data or None if not found
        """
        key = build_cache_key("word", word)
        try:
            cached = await self.redis.get(key)
            if cached:
                logger.debug(f"Cache HIT for word: {word}")
                return json.loads(cached)
            logger.debug(f"Cache MISS for word: {word}")
            return None
        except Exception as e:
            logger.error(f"Redis get error for {word}: {e}")
            return None

    async def set_cached_word(
        self,
        word: str,
        data: dict[str, Any],
        frequency_rank: Optional[int] = None
    ) -> bool:
        """
        Set cached word data with appropriate TTL.

        Args:
            word: Word text (normalized)
            data: Word data to cache
            frequency_rank: Word frequency rank (for TTL determination)

        Returns:
            True if successfully cached
        """
        key = build_cache_key("word", word)

        # Determine TTL based on word frequency
        if frequency_rank and frequency_rank <= 5000:
            # Common words: no expiration
            ttl = settings.cache_ttl_common_words
        else:
            # Less common words: 30-day TTL
            ttl = settings.cache_ttl_less_common

        try:
            serialized = json.dumps(data)
            if ttl > 0:
                await self.redis.setex(key, ttl, serialized)
            else:
                await self.redis.set(key, serialized)
            logger.debug(f"Cached word: {word} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis set error for {word}: {e}")
            return False

    async def set_failed_lookup(self, word: str) -> bool:
        """
        Cache failed lookup to prevent repeated API calls.

        Args:
            word: Word text that was not found

        Returns:
            True if successfully cached
        """
        key = build_cache_key("failed", word)
        try:
            await self.redis.setex(
                key,
                settings.cache_ttl_failed_lookups,
                "not_found"
            )
            return True
        except Exception as e:
            logger.error(f"Redis set error for failed lookup {word}: {e}")
            return False

    async def is_failed_lookup(self, word: str) -> bool:
        """
        Check if word lookup previously failed.

        Args:
            word: Word text to check

        Returns:
            True if word is in failed lookup cache
        """
        key = build_cache_key("failed", word)
        try:
            exists = await self.redis.exists(key)
            return exists > 0
        except Exception as e:
            logger.error(f"Redis exists error for {word}: {e}")
            return False

    async def invalidate_word_cache(self, word: str) -> bool:
        """
        Invalidate cached word data.

        Args:
            word: Word text to invalidate

        Returns:
            True if cache was invalidated
        """
        key = build_cache_key("word", word)
        try:
            deleted = await self.redis.delete(key)
            logger.info(f"Invalidated cache for word: {word}")
            return deleted > 0
        except Exception as e:
            logger.error(f"Redis delete error for {word}: {e}")
            return False
