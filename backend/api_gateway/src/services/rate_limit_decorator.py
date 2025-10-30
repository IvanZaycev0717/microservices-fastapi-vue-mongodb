from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, Request, status
from services.token_bucket import TokenBucket
from services.dependencies import get_client_identifier
from logger import get_logger

logger = get_logger("rate_limit_decorator")


def rate_limited():
    """Decorator for applying rate limiting to endpoint functions.

    Automatically detects Request and TokenBucket dependencies in function
    arguments and applies rate limiting based on client identifier.

    Returns:
        Callable: Decorator function that wraps the original function with rate limiting logic.

    Note:
        - Extracts client identifier from the Request object
        - Automatically finds TokenBucket instance from function kwargs
        - Skips rate limiting if Request or TokenBucket are not available
        - Raises HTTP 429 exception when rate limit is exceeded
        - Logs rate limiting decisions for monitoring purposes
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            request = None
            for arg in kwargs.values():
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                logger.warning(
                    "No Request object found in kwargs - skipping rate limiting"
                )
                return await func(*args, **kwargs)

            token_bucket = None
            identifier = get_client_identifier(request)
            logger.info(f"Rate limiting check for: {identifier}")

            for arg_name, arg_value in kwargs.items():
                if isinstance(arg_value, TokenBucket):
                    token_bucket = arg_value
                    break

            if not token_bucket:
                logger.warning(
                    "No TokenBucket found in kwargs - skipping rate limiting"
                )
                return await func(*args, **kwargs)

            allowed = await token_bucket.acquire(identifier)
            if not allowed:
                logger.warning(f"Rate limit exceeded for: {identifier}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                )

            logger.info(f"Rate limit allowed for: {identifier}")
            return await func(*args, **kwargs)

        return wrapper

    return decorator
