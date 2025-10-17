from fastapi import Request, Depends
from redis import Redis
from services.redis_connect_management import RedisDatabase
from services.cache_service import CacheService


def get_redis_cache(request: Request) -> Redis:
    return request.app.state.redis_manager.get_client(RedisDatabase.CACHE)


def get_cache_service(redis_client=Depends(get_redis_cache)) -> CacheService:
    return CacheService(redis_client)
