from fastapi import Request, Depends
from redis import Redis
from services.redis_connect_management import RedisDatabase


def get_redis_cache(request: Request) -> Redis:
    """Dependency to get cache Redis client.

    Returns:
        Redis client configured for cache database.
    """
    return request.app.state.redis_manager.get_client(RedisDatabase.CACHE)


def get_redis_rate_limiter(request: Request) -> Redis:
    """Dependency to get rate limiter Redis client.

    Returns:
        Redis client configured for rate limiting database.
    """
    return request.app.state.redis_manager.get_client(
        RedisDatabase.RATE_LIMITER
    )
