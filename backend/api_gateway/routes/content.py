from fastapi import APIRouter

from services.content_service import ContentService

router = APIRouter(prefix="/content", tags=["content"])
content_service = ContentService()


@router.get("/about")
async def get_about():
    return await content_service.get_about()


@router.get("/technologies")
async def technologies():
    return {"Content": "technologies"}


@router.get("/certificates")
async def certificates():
    return {"Content": "certificates"}


@router.get("/projects")
async def projects():
    return {"Content": "projects"}


@router.get("/publications")
async def publications():
    return {"Content": "publications"}
