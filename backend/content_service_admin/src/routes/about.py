import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status


from services.crud.about import AboutCRUD
from models.about import CreateAboutRequest, AboutFullResponse, AboutTranslatedResponse
from dependencies import get_logger_dependency

router = APIRouter(prefix="/about", tags=["about"])


async def get_about_crud(request: Request) -> AboutCRUD:
    db = request.app.state.mongo_db
    return AboutCRUD(db)


@router.get("/", response_model=list[AboutFullResponse] | list[AboutTranslatedResponse])
async def get_about_content(
    lang: Optional[str] = Query(None),
    about_crud: AboutCRUD = Depends(get_about_crud),
    logger: logging.Logger = Depends(get_logger_dependency),
):
    try:
        result = await about_crud.read_all(lang)
        if not result:
            raise HTTPException(status_code=404, detail="About content not found")
        logger.info("About collection fetched successfully")
        return result
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching about content"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_about_content(
    request: CreateAboutRequest, about_crud: AboutCRUD = Depends(get_about_crud)
):
    result = await about_crud.create(request.model_dump(exclude_none=True))
    return f"A new document with _id={result} was created"
