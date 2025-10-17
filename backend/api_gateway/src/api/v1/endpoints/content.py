from fastapi import APIRouter, HTTPException, Query, Depends, Request, status
from grpc import RpcError
import grpc
from grpc_clients.content_service import ContentClient

from services.cache_decorator import cache_response

from logger import get_logger
from services.rate_limit_decorator import rate_limited
from services.dependencies import (
    get_token_bucket,
)
from services.token_bucket import TokenBucket
from services.cache_service import CacheService
from services.cache_dependencies import get_cache_service

router = APIRouter()
logger = get_logger("ContentEndpoints")
content_client = ContentClient()


@router.get("/about")
@rate_limited()
@cache_response(key_prefix="content")
async def get_about(
    request: Request,
    lang: str = Query(None),
    cache_service: CacheService = Depends(get_cache_service),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve about page content with optional language and caching.

    Args:
        lang (str, optional): Language code for localized content. Defaults to None.
        cache_service (CacheService): Cache service dependency for response caching.

    Returns:
        dict: Dictionary containing about page content items.

    Raises:
        HTTPException:
            - 500: If content service is unavailable or internal error occurs

    Note:
        - Uses response caching with dynamic key based on language parameter
        - Returns empty list if no about content found for specified language
        - Each about item contains image, title, and description
    """
    try:
        response = content_client.get_about(lang)
        return {
            "about": [
                {
                    "image_url": item.image_url,
                    "title": item.title,
                    "description": item.description,
                }
                for item in response.about
            ]
        }
    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return {"about": []}
        logger.exception(f"gRPC error in get_about {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_about {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/tech")
@rate_limited()
@cache_response(key_prefix="content")
async def get_tech(
    request: Request,
    cache_service: CacheService = Depends(get_cache_service),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve technology stack information with caching.

    Args:
        cache_service (CacheService): Cache service dependency for response caching.

    Returns:
        dict: Dictionary containing technology kingdoms and their items.

    Raises:
        HTTPException:
            - 500: If content service is unavailable or internal error occurs

    Note:
        - Uses response caching to improve performance for static technology data
        - Organizes technologies into kingdoms/categories with associated items
        - Returns hierarchical structure of technology stack
    """
    try:
        response = content_client.get_tech()
        return {
            "kingdoms": [
                {"kingdom": kingdom.kingdom, "items": list(kingdom.items)}
                for kingdom in response.kingdoms
            ]
        }
    except RpcError as e:
        logger.exception(f"gRPC error in get_tech {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_tech {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/projects")
@rate_limited()
@cache_response(key_prefix="content")
async def get_projects(
    request: Request,
    lang: str = Query("en"),
    sort: str = Query("date_desc"),
    cache_service: CacheService = Depends(get_cache_service),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve projects list with language, sorting and caching.

    Args:
        lang (str): Language code for localized project content. Defaults to "en".
        sort (str): Sorting criteria for projects. Defaults to "date_desc".
        cache_service (CacheService): Cache service dependency for response caching.

    Returns:
        dict: Dictionary containing list of projects with details.

    Raises:
        HTTPException:
            - 500: If content service is unavailable or internal error occurs

    Note:
        - Uses response caching with dynamic key based on language and sort parameters
        - Returns comprehensive project data including thumbnails, descriptions and metadata
        - Supports different sorting options and language localizations
    """
    try:
        response = content_client.get_projects(lang, sort)
        return {
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
    except RpcError as e:
        logger.exception(f"gRPC error in get_projects {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_projects {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/certificates")
@rate_limited()
@cache_response(key_prefix="content")
async def get_certificates(
    request: Request,
    sort: str = Query("date_desc"),
    cache_service: CacheService = Depends(get_cache_service),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve certificates list with sorting and caching.

    Args:
        sort (str): Sorting criteria for certificates. Defaults to "date_desc".
        cache_service (CacheService): Cache service dependency for response caching.

    Returns:
        dict: Dictionary containing list of certificates with details.

    Raises:
        HTTPException:
            - 500: If content service is unavailable or internal error occurs

    Note:
        - Uses response caching with dynamic key based on sort parameter
        - Returns certificate data including thumbnails, source images and metadata
        - Supports different sorting options for certificate display
    """
    try:
        response = content_client.get_certificates(sort)
        return {
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
    except RpcError as e:
        logger.exception(f"gRPC error in get_certificates {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_certificates {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/publications")
@rate_limited()
@cache_response(key_prefix="content")
async def get_publications(
    request: Request,
    lang: str = Query("en"),
    sort: str = Query("date_desc"),
    cache_service: CacheService = Depends(get_cache_service),
    token_bucket: TokenBucket = Depends(get_token_bucket),
):
    """
    Retrieve publications list with language, sorting and caching.

    Args:
        lang (str): Language code for localized publication content. Defaults to "en".
        sort (str): Sorting criteria for publications. Defaults to "date_desc".
        cache_service (CacheService): Cache service dependency for response caching.

    Returns:
        dict: Dictionary containing list of publications with details.

    Raises:
        HTTPException:
            - 500: If content service is unavailable or internal error occurs

    Note:
        - Uses response caching with dynamic key based on language and sort parameters
        - Returns publication data including titles, site information and ratings
        - Supports different sorting options and language localizations
    """
    try:
        response = content_client.get_publications(lang, sort)
        return {
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
    except RpcError as e:
        logger.exception(f"gRPC error in get_publications {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_publications {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
