from fastapi import Request, Depends
from redis import Redis
from services.redis_connect_management import RedisDatabase
from services.token_bucket import TokenBucket
from settings import settings
from logger import get_logger


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


def get_token_bucket(
    redis_client: Redis = Depends(get_redis_rate_limiter),
) -> TokenBucket:
    """Dependency to get default TokenBucket instance."""
    logger = get_logger("TokenBucketDependency")
    logger.info("Creating default TokenBucket for rate limiting")
    return TokenBucket(
        redis_client=redis_client,
        capacity=settings.RATE_LIMIT_CAPACITY,
        refill_rate=settings.RATE_LIMIT_REFILL_RATE,
    )


def get_auth_token_bucket(
    redis_client: Redis = Depends(get_redis_rate_limiter),
) -> TokenBucket:
    """Dependency to get Auth TokenBucket instance with stricter limits."""
    logger = get_logger("TokenBucketDependency")
    logger.info("Creating Auth TokenBucket with stricter limits")
    return TokenBucket(
        redis_client=redis_client,
        capacity=settings.AUTH_RATE_LIMIT_CAPACITY,
        refill_rate=settings.AUTH_RATE_LIMIT_REFILL_RATE,
    )


def get_comments_token_bucket(
    redis_client: Redis = Depends(get_redis_rate_limiter),
) -> TokenBucket:
    """Dependency to get Comments TokenBucket instance."""
    logger = get_logger("TokenBucketDependency")
    logger.info("Creating Comments TokenBucket for rate limiting")
    return TokenBucket(
        redis_client=redis_client,
        capacity=settings.COMMENTS_RATE_LIMIT_CAPACITY,
        refill_rate=settings.COMMENTS_RATE_LIMIT_REFILL_RATE,
    )


def get_client_identifier(request: Request) -> str:
    """Dependency to get client identifier for rate limiting.

    Args:
        request: FastAPI request object.

    Returns:
        Client identifier (IP address + endpoint path).
    """
    client_ip = request.client.host if request.client else "unknown"
    endpoint_path = request.url.path
    return f"ip:{client_ip}:{endpoint_path}"
