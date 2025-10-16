from fastapi import APIRouter, HTTPException, Query, Depends, status
from grpc import RpcError
import grpc
from grpc_clients.content_service import ContentClient
from services.cache_service import CacheService
from services.cache_decorator import cache_response
from services.dependencies import get_redis_cache
from logger import get_logger

router = APIRouter()
logger = get_logger("ContentEndpoints")
content_client = ContentClient()


def get_cache_service(redis_client=Depends(get_redis_cache)) -> CacheService:
    """Dependency to get CacheService instance."""
    return CacheService(redis_client)


@router.get("/about")
@cache_response(key_prefix="content")
async def get_about(
    lang: str = Query(None),
    cache_service: CacheService = Depends(get_cache_service),
):
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
@cache_response(key_prefix="content")
async def get_tech(cache_service: CacheService = Depends(get_cache_service)):
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
@cache_response(key_prefix="content")
async def get_projects(
    lang: str = Query("en"),
    sort: str = Query("date_desc"),
    cache_service: CacheService = Depends(get_cache_service),
):
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
@cache_response(key_prefix="content")
async def get_certificates(
    sort: str = Query("date_desc"),
    cache_service: CacheService = Depends(get_cache_service),
):
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
@cache_response(key_prefix="content")
async def get_publications(
    lang: str = Query("en"),
    sort: str = Query("date_desc"),
    cache_service: CacheService = Depends(get_cache_service),
):
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
