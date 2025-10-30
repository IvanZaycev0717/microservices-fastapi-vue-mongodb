from functools import wraps
from typing import Any, Callable
from fastapi import Request
from services.cache_service import CacheService
from logger import get_logger
from services.token_bucket import TokenBucket

logger = get_logger("CacheDecorator")


async def _get_cache_service_from_request(request: Request) -> CacheService:
    """Helper to get CacheService from request without circular imports."""
    from services.redis_connect_management import RedisDatabase

    redis_client = await request.app.state.redis_manager.get_client(
        RedisDatabase.CACHE
    )
    return CacheService(redis_client)


def cache_response(key_prefix: str):
    """Decorator for caching function responses in Redis.

    Generates cache keys based on function name and arguments, automatically
    handles cache retrieval and storage.

    Args:
        key_prefix: Base string for cache key generation.

    Returns:
        Callable: Decorator function that wraps the original function with caching logic.

    Note:
        - First tries to find CacheService in function kwargs
        - Falls back to creating CacheService from request if available
        - Skips caching entirely if no CacheService can be obtained
        - Excludes certain argument types from cache key generation
        - Uses colon-separated cache key format
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            cache_service = None
            for arg_value in kwargs.values():
                if isinstance(arg_value, CacheService):
                    cache_service = arg_value
                    break

            if not cache_service:
                request = None
                for arg in kwargs.values():
                    if isinstance(arg, Request):
                        request = arg
                        break

                if request:
                    try:
                        cache_service = await _get_cache_service_from_request(
                            request
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to get CacheService from request: {e}"
                        )
                        cache_service = None

            if not cache_service:
                logger.warning("CacheService not available - skipping caching")
                return await func(*args, **kwargs)

            cache_key_parts = [key_prefix, func.__name__]

            for key, value in kwargs.items():
                if (
                    not isinstance(value, (CacheService, TokenBucket, Request))
                    and value is not None
                    and not key.startswith("_")
                ):
                    cache_key_parts.append(f"{key}={value}")

            cache_key = ":".join(cache_key_parts)

            try:
                cached_result = await cache_service.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
            except Exception as e:
                logger.error(f"Cache get error for key {cache_key}: {e}")

            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)

            try:
                await cache_service.set(cache_key, result)
            except Exception as e:
                logger.error(f"Cache set error for key {cache_key}: {e}")

            return result

        return wrapper

    return decorator
