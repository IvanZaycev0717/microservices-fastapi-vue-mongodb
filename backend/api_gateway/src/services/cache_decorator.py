from functools import wraps
from typing import Any, Callable
from services.cache_service import CacheService
from logger import get_logger

logger = get_logger("CacheDecorator")


def cache_response(key_prefix: str):
    """
    Decorator for caching responses in Redis with dynamic key generation.

    The decorator automatically injects cache logic for async functions. It looks
    for a CacheService instance in the function kwargs and uses it for cache operations.
    Cache keys are built from the prefix, function name, and non-CacheService kwargs.

    Args:
        key_prefix (str): Prefix for cache keys to namespace different types of data.

    Returns:
        Callable: Decorator function that wraps the original function with caching logic.

    Example:
        ```python
        @cache_response("users")
        async def get_user(user_id: int, cache_service: CacheService):
            # Function implementation
        ```

    Note:
        - If no CacheService is found in kwargs, the original function is called without caching
        - None values in kwargs are excluded from cache key generation
        - Cache keys format: "prefix:function_name:key1=value1:key2=value2"
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
                if not isinstance(value, CacheService) and value is not None:
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
