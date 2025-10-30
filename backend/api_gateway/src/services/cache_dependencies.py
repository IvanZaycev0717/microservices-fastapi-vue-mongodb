from fastapi import Request, Depends
from redis import Redis
from services.redis_connect_management import RedisDatabase
from services.cache_service import CacheService


def get_redis_cache(request: Request) -> Redis:
    """Retrieves a Redis client instance for cache operations.

    This dependency function extracts the Redis cache client from the
    application state in the request object.

    Args:
        request: The FastAPI Request object containing application state.

    Returns:
        Redis: A Redis client instance configured for cache operations.
    """
    return request.app.state.redis_manager.get_client(RedisDatabase.CACHE)


def get_cache_service(redis_client=Depends(get_redis_cache)) -> CacheService:
    """Dependency provider for CacheService instance.

    Injects a Redis client dependency and returns a configured CacheService.

    Args:
        redis_client: Redis client instance provided by dependency injection.

    Returns:
        CacheService: A CacheService instance initialized with the Redis client.
    """
    return CacheService(redis_client)
