from functools import wraps
from typing import Any, Callable

from fastapi import Request
from services.cache_service import CacheService
from logger import get_logger
from services.token_bucket import TokenBucket

logger = get_logger("CacheDecorator")


def cache_response(key_prefix: str):
    """Decorator for caching function responses in Redis.

    Generates cache keys based on function name and arguments, automatically
    handles cache retrieval and storage, and injects CacheService dependency.

    Args:
        key_prefix: Base string for cache key generation.

    Returns:
        Callable: Decorator function that wraps the original function with caching logic.

    Note:
        - Automatically detects CacheService instance from function kwargs
        - Skips caching if no CacheService is available
        - Excludes certain argument types from cache key (CacheService, TokenBucket, Request)
        - Uses colon-separated cache key format: key_prefix:function_name:arg1=val1:arg2=val2
        - Logs cache hits and misses for debugging purposes
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

            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result)

            return result

        return wrapper

    return decorator
