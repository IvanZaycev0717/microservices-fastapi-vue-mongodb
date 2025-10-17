from functools import wraps
from typing import Any, Callable

from fastapi import Request
from services.cache_service import CacheService
from logger import get_logger
from services.token_bucket import TokenBucket

logger = get_logger("CacheDecorator")


def cache_response(key_prefix: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Find cache_service in kwargs
            cache_service = None
            for arg_value in kwargs.values():
                if isinstance(arg_value, CacheService):
                    cache_service = arg_value
                    break

            if not cache_service:
                return await func(*args, **kwargs)

            # Generate normalized cache key
            cache_key_parts = [key_prefix, func.__name__]

            # Include only relevant query parameters, exclude service objects
            for key, value in kwargs.items():
                # Exclude service objects and None values from key generation
                if (
                    not isinstance(value, (CacheService, TokenBucket, Request))
                    and value is not None
                    and not key.startswith("_")
                ):
                    cache_key_parts.append(f"{key}={value}")

            cache_key = ":".join(cache_key_parts)

            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            # Execute function and cache result
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result)

            return result

        return wrapper

    return decorator
