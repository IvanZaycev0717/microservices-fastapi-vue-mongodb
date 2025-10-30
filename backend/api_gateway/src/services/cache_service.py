from redis.asyncio import Redis
from typing import Any
import json
from logger import get_logger
from settings import settings
from services.utils import convert_minutes_to_seconds

logger = get_logger("CacheService")


class CacheService:
    """Service for handling Redis cache operations."""

    def __init__(self, redis_client: Redis):
        """
        Initialize the CacheService with Redis client and TTL configuration.

        Args:
            redis_client (Redis): Redis client instance for cache operations.

        Attributes:
            redis (Redis): Redis client instance for performing cache operations.
            ttl (int): Time-to-live for cache entries in seconds, converted from minutes.
        """
        self.redis = redis_client
        self.ttl = convert_minutes_to_seconds(settings.CACHE_TTL_MINUTES)

    async def get(self, key: str) -> Any | None:
        """
        Retrieve a value from cache by key.

        Args:
            key (str): The cache key to retrieve.

        Returns:
            Any | None: The deserialized JSON value if found, None if key doesn't exist
                        or an error occurs.

        Raises:
            Exception: Logs any exceptions that occur during cache retrieval but returns
                       None to allow graceful degradation.
        """
        try:
            cached = await self.redis.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.exception(f"Cache get error for key {key} - {e}")
            return None

    async def set(self, key: str, value: Any) -> bool:
        """
        Store a value in cache with TTL.

        Args:
            key (str): The cache key to store the value under.
            value (Any): The value to be cached (will be serialized to JSON).

        Returns:
            bool: True if the value was successfully cached, False if an error occurred.

        Raises:
            Exception: Logs any exceptions that occur during cache storage but returns
                       False to allow graceful degradation.
        """
        try:
            serialized = json.dumps(value)
            await self.redis.setex(key, self.ttl, serialized)
            return True
        except Exception as e:
            logger.exception(f"Cache set error for key {key} - {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key (str): The cache key to delete.

        Returns:
            bool: True if the key was successfully deleted, False if the key didn't exist
                  or an error occurred.

        Raises:
            Exception: Logs any exceptions that occur during cache deletion but returns
                       False to allow graceful degradation.
        """
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.exception(f"Cache delete error for key {key} - {e}")
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """
        Delete all cache keys matching a pattern in batches.

        This method scans for keys matching the given pattern and deletes them in batches
        to avoid blocking the Redis server with large deletions.

        Args:
            pattern (str): The pattern to match keys against (e.g., "users:*", "cache:*").

        Returns:
            bool: True if all matching keys were successfully deleted or no keys were found,
                  False if an error occurred during the operation.

        Raises:
            Exception: Logs any exceptions that occur during pattern clearing but returns
                       False to allow graceful degradation.

        Note:
            - Uses SCAN instead of KEYS to avoid blocking Redis with large key sets
            - Processes deletions in batches of 100 keys to maintain performance
            - Logs detailed information about the deletion process for monitoring
        """
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            logger.info(
                f"Found {len(keys)} keys to delete for pattern: {pattern}"
            )

            if keys:
                deleted_count = 0
                for i in range(0, len(keys), 100):  # Batch size 100
                    batch = keys[i : i + 100]
                    result = await self.redis.delete(*batch)
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
            logger.exception(f"Cache clear pattern error for {pattern} - {e}")
            return False
