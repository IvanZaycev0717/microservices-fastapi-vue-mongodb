import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Form


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
    image: str = Form(
        description="URL изображения", json_schema_extra={"example": "image_N.jpg"}
    ),
    title_en: str = Form(
        description="Заголовок на английском",
        json_schema_extra={"example": "Some title 1 EN"},
    ),
    description_en: str = Form(
        description="Описание на английском",
        json_schema_extra={"example": "Some description 1 EN"},
    ),
    title_ru: str = Form(
        description="Заголовок на русском",
        json_schema_extra={"example": "Название 1 RU"},
    ),
    description_ru: str = Form(
        description="Описание на русском",
        json_schema_extra={"example": "Описание 1 RU"},
    ),
    about_crud: AboutCRUD = Depends(get_about_crud),
):
    data = CreateAboutRequest(
        image=image,
        translations={
            "en": {"title": title_en, "description": description_en},
            "ru": {"title": title_ru, "description": description_ru},
        },
    )
    result = await about_crud.create(data.model_dump(exclude_none=True))
    return f"Document created with _id={result}"
