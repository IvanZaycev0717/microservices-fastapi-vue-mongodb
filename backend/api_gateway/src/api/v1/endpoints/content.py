from fastapi import APIRouter, HTTPException, Query, Depends, Request, status
from grpc import RpcError
import grpc
from grpc_clients.content_service import ContentClient
from logger import get_logger
from services.rate_limit_decorator import rate_limited
from services.dependencies import get_token_bucket, get_redis_cache
from services.token_bucket import TokenBucket
from services.cache_service import CacheService

router = APIRouter()
logger = get_logger("ContentEndpoints")
content_client = ContentClient()


@router.get("/about")
@rate_limited()
async def get_about(
    request: Request,
    lang: str = Query(None),
    redis_cache=Depends(get_redis_cache),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve about page content with caching.

    Args:
        lang: Language code for localized content.
        redis_cache: Redis client for caching.
        token_bucket: Rate limiting token bucket.

    Returns:
        dict: About page content.

    Raises:
        HTTPException: 500 if service unavailable
    """
    cache_service = CacheService(redis_cache)
    cache_key = f"content:about:lang={lang or 'default'}"

    cached = await cache_service.get(cache_key)
    if cached is not None:
        logger.info(f"Cache hit for {cache_key}")
        return cached

    try:
        response = content_client.get_about(lang)
        result = {
            "about": [
                {
                    "image_url": item.image_url,
                    "title": item.title,
                    "description": item.description,
                }
                for item in response.about
            ]
        }

        await cache_service.set(cache_key, result)
        logger.info(f"Cached data for {cache_key}")

        return result

    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            result = {"about": []}
            await cache_service.set(cache_key, result)  # Cache empty result
            return result
        logger.exception(f"gRPC error in get_about: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_about: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/tech")
@rate_limited()
async def get_tech(
    request: Request,
    redis_cache=Depends(get_redis_cache),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve technology stack information with caching.
    """
    cache_service = CacheService(redis_cache)
    cache_key = "content:tech"

    cached = await cache_service.get(cache_key)
    if cached is not None:
        logger.info(f"Cache hit for {cache_key}")
        return cached

    try:
        response = content_client.get_tech()
        result = {
            "kingdoms": [
                {"kingdom": kingdom.kingdom, "items": list(kingdom.items)}
                for kingdom in response.kingdoms
            ]
        }

        await cache_service.set(cache_key, result)
        logger.info(f"Cached data for {cache_key}")

        return result

    except RpcError as e:
        logger.exception(f"gRPC error in get_tech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_tech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/projects")
@rate_limited()
async def get_projects(
    request: Request,
    lang: str = Query("en"),
    sort: str = Query("date_desc"),
    redis_cache=Depends(get_redis_cache),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve projects list with language, sorting and caching.
    """
    cache_service = CacheService(redis_cache)
    cache_key = f"content:projects:lang={lang}:sort={sort}"

    cached = await cache_service.get(cache_key)
    if cached is not None:
        logger.info(f"Cache hit for {cache_key}")
        return cached

    try:
        response = content_client.get_projects(lang, sort)
        result = {
            "projects": [
                {
                    "id": project.id,
                    "title": project.title,
                    "thumbnail": project.thumbnail,
                    "image": project.image,
                    "description": project.description,
                    "link": project.link,
                    "date": project.date,
                    "popularity": project.popularity,
                }
                for project in response.projects
            ]
        }

        await cache_service.set(cache_key, result)
        logger.info(f"Cached data for {cache_key}")

        return result

    except RpcError as e:
        logger.exception(f"gRPC error in get_projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/certificates")
@rate_limited()
async def get_certificates(
    request: Request,
    sort: str = Query("date_desc"),
    redis_cache=Depends(get_redis_cache),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve certificates list with sorting and caching.
    """
    cache_service = CacheService(redis_cache)
    cache_key = f"content:certificates:sort={sort}"

    cached = await cache_service.get(cache_key)
    if cached is not None:
        logger.info(f"Cache hit for {cache_key}")
        return cached

    try:
        response = content_client.get_certificates(sort)
        result = {
            "certificates": [
                {
                    "id": cert.id,
                    "thumb": cert.thumb,
                    "src": cert.src,
                    "date": cert.date,
                    "popularity": cert.popularity,
                    "alt": cert.alt,
                }
                for cert in response.certificates
            ]
        }

        await cache_service.set(cache_key, result)
        logger.info(f"Cached data for {cache_key}")

        return result

    except RpcError as e:
        logger.exception(f"gRPC error in get_certificates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_certificates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/publications")
@rate_limited()
async def get_publications(
    request: Request,
    lang: str = Query("en"),
    sort: str = Query("date_desc"),
    redis_cache=Depends(get_redis_cache),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve publications list with language, sorting and caching.
    """
    cache_service = CacheService(redis_cache)
    cache_key = f"content:publications:lang={lang}:sort={sort}"

    cached = await cache_service.get(cache_key)
    if cached is not None:
        logger.info(f"Cache hit for {cache_key}")
        return cached

    try:
        response = content_client.get_publications(lang, sort)
        result = {
            "publications": [
                {
                    "id": pub.id,
                    "title": pub.title,
                    "page": pub.page,
                    "site": pub.site,
                    "rating": pub.rating,
                    "date": pub.date,
                }
                for pub in response.publications
            ]
        }

        await cache_service.set(cache_key, result)
        logger.info(f"Cached data for {cache_key}")

        return result

    except RpcError as e:
        logger.exception(f"gRPC error in get_publications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_publications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
