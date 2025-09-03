import logging
import re
import uuid
from pathlib import Path
from typing import Annotated, Optional

from fastapi import (APIRouter, Depends, File, Form, HTTPException, Query,
                     Request, UploadFile, status)
from pydantic import ValidationError

from dependencies import get_logger_dependency
from models.about import (AboutFullResponse, AboutTranslatedResponse,
                          CreateAboutRequest)
from services.crud.about import AboutCRUD
from services.image_processor import (generate_image_filename,
                                      has_image_allowed_extention,
                                      has_image_proper_size_kb, resize_image,
                                      save_image_as_webp)
from settings import settings

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
    image: UploadFile = File(description="Изображение для загрузки"),
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
    logger: logging.Logger = Depends(get_logger_dependency),
):
    try:
        if not await has_image_allowed_extention(image):
            error_message = "Image invalid format"
            logger.error(error_message)
            raise HTTPException(400, error_message)
        if not await has_image_proper_size_kb(image):
            error_message = "Image size exceeds 500KB"
            logger.error(error_message)
            raise HTTPException(400, error_message)
        resized_image = await resize_image(image)
        filename = await generate_image_filename(resized_image)
        image_url = await save_image_as_webp(
            resized_image, settings.ABOUT_IMAGES_PATH, settings.ABOUT_STR, filename
        )
        data = CreateAboutRequest(
            image_url=image_url,
            translations={
                "en": {"title": title_en, "description": description_en},
                "ru": {"title": title_ru, "description": description_ru},
            },
        )

        result = await about_crud.create(data.model_dump(exclude_none=True))
        logger.info(f"Document created with _id={result}")
        return f"Document created with _id={result}"

    except HTTPException:
        raise

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(422, detail=e.errors())

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(500, detail="Internal server error")
