from enum import Enum
from redis import Redis
from redis.exceptions import RedisError
from logger import get_logger
from settings import settings

logger = get_logger("RedisManager")


class RedisDatabase(Enum):
    """Redis database types."""

    CACHE = 0
    RATE_LIMITER = 1


class RedisManager:
    """Manager for Redis connection lifecycle.

    Handles connection establishment and cleanup for different database types.
    """

    def __init__(self):
        self._clients: dict[RedisDatabase, Redis] = {}

    async def connect(self):
        """Establish connections to all Redis databases."""
        try:
            for db_type in RedisDatabase:
                client = self._create_client(db_type)
                client.ping()
                self._clients[db_type] = client

            logger.info("All Redis connections established successfully")
        except RedisError as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    def _create_client(self, db_type: RedisDatabase) -> Redis:
        """Create Redis client for specific database type.

        Args:
            db_type: Type of database to create client for.

        Returns:
            Configured Redis client instance.
        """
        match db_type:
            case RedisDatabase.CACHE:
                return Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_CACHE_DB,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                )
            case RedisDatabase.RATE_LIMITER:
                return Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_RATE_LIMIT_DB,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                )

    def get_client(self, db_type: RedisDatabase) -> Redis:
        """Get Redis client for specific database type.

        Args:
            db_type: Type of database to get client for.

        Returns:
            Redis client instance.

        Raises:
            ValueError: If client for specified type is not found.
        """
        if client := self._clients.get(db_type):
            return client
        raise ValueError(f"No client found for database type: {db_type}")

    async def disconnect(self):
        """Close all Redis connections and cleanup resources."""
        for client in self._clients.values():
            client.close()
        logger.info("All Redis connections closed")


redis_manager = RedisManager()
