from fastapi import APIRouter, HTTPException, Query
from grpc import RpcError

from grpc_clients.content_service import ContentClient
from logger import get_logger

router = APIRouter()
logger = get_logger("ContentEndpoints")
content_client = ContentClient()


@router.get("/about")
async def get_about(lang: str = Query(None)):
    try:
        response = content_client.get_about(lang)
        return {"about": [{
            "id": item.id,
            "image_url": item.image_url,
            "title": item.title,
            "description": item.description
        } for item in response.about]}
    except RpcError as e:
        logger.error(f"gRPC error in get_about: {e.code()} - {e.details()}")
        raise HTTPException(status_code=500, detail="Content service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in get_about: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tech")
async def get_tech():
    try:
        response = content_client.get_tech()
        return {"kingdoms": [{
            "kingdom": kingdom.kingdom,
            "items": list(kingdom.items)
        } for kingdom in response.kingdoms]}
    except RpcError as e:
        logger.error(f"gRPC error in get_tech: {e.code()} - {e.details()}")
        raise HTTPException(status_code=500, detail="Content service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in get_tech: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/projects")
async def get_projects(lang: str = Query("en"), sort: str = Query("date_desc")):
    try:
        response = content_client.get_projects(lang, sort)
        return {"projects": [{
            "id": project.id,
            "title": project.title,
            "thumbnail": project.thumbnail,
            "image": project.image,
            "description": project.description,
            "link": project.link,
            "date": project.date,
            "popularity": project.popularity
        } for project in response.projects]}
    except RpcError as e:
        logger.error(f"gRPC error in get_projects: {e.code()} - {e.details()}")
        raise HTTPException(status_code=500, detail="Content service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in get_projects: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/certificates")
async def get_certificates(sort: str = Query("date_desc")):
    try:
        response = content_client.get_certificates(sort)
        return {"certificates": [{
            "id": cert.id,
            "thumb": cert.thumb,
            "src": cert.src,
            "date": cert.date,
            "popularity": cert.popularity,
            "alt": cert.alt
        } for cert in response.certificates]}
    except RpcError as e:
        logger.error(f"gRPC error in get_certificates: {e.code()} - {e.details()}")
        raise HTTPException(status_code=500, detail="Content service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in get_certificates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/publications")
async def get_publications(lang: str = Query("en"), sort: str = Query("date_desc")):
    try:
        response = content_client.get_publications(lang, sort)
        return {"publications": [{
            "id": pub.id,
            "title": pub.title,
            "page": pub.page,
            "site": pub.site,
            "rating": pub.rating,
            "date": pub.date
        } for pub in response.publications]}
    except RpcError as e:
        logger.error(f"gRPC error in get_publications: {e.code()} - {e.details()}")
        raise HTTPException(status_code=500, detail="Content service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in get_publications: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")