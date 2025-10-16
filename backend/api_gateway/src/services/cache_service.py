from redis import Redis
from typing import Any
import json
from logger import get_logger
from settings import settings
from services.utils import convert_minutes_to_seconds

logger = get_logger("CacheService")


class CacheService:
    """Service for handling Redis cache operations."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = convert_minutes_to_seconds(settings.CACHE_TTL_MINUTES)

    async def get(self, key: str) -> Any | None:
        """Get value from cache by key.

        Args:
            key: Cache key to retrieve.

        Returns:
            Deserialized value or None if not found.
        """
        try:
            cached = self.redis.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.exception(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any) -> bool:
        """Set value in cache with TTL.

        Args:
            key: Cache key to set.
            value: Value to cache (must be JSON serializable).

        Returns:
            True if successful, False otherwise.
        """
        try:
            serialized = json.dumps(value)
            self.redis.setex(key, self.ttl, serialized)
            return True
        except Exception as e:
            logger.exception(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key to delete.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.exception(f"Cache delete error for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """Delete all keys matching pattern.

        Args:
            pattern: Redis pattern to match keys.

        Returns:
            True if successful, False otherwise.
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.exception(f"Cache clear pattern error for {pattern}: {e}")
            return False
