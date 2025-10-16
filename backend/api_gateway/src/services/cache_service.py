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
        """Get value from cache by key."""
        try:
            cached = self.redis.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.exception(f"Cache get error for key {key}")
            return None

    async def set(self, key: str, value: Any) -> bool:
        """Set value in cache with TTL."""
        try:
            serialized = json.dumps(value)
            self.redis.setex(key, self.ttl, serialized)
            return True
        except Exception as e:
            logger.exception(f"Cache set error for key {key}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            result = self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.exception(f"Cache delete error for key {key}")
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """Delete all keys matching pattern."""
        try:
            keys = []
            for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            logger.info(
                f"Found {len(keys)} keys to delete for pattern: {pattern}"
            )

            if keys:
                # Delete keys in batches to avoid blocking
                deleted_count = 0
                for i in range(0, len(keys), 100):  # Batch size 100
                    batch = keys[i : i + 100]
                    result = self.redis.delete(*batch)
                    deleted_count += result
                    logger.info(f"Deleted batch: {result} keys")

                logger.info(
                    f"Total deleted: {deleted_count} keys for pattern: {pattern}"
                )
                return deleted_count > 0
            else:
                logger.info(f"No keys found for pattern: {pattern}")
                return True

        except Exception as e:
            logger.exception(f"Cache clear pattern error for {pattern}")
            return False
