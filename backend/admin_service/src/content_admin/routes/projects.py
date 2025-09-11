import logging
from enum import StrEnum
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.encoders import ENCODERS_BY_TYPE

from content_admin.crud.projects import ProjectsCRUD
from content_admin.dependencies import (get_logger_dependency, get_minio_crud,
                                        get_projects_crud)
from content_admin.models.projects import ProjectCreateForm
from services.image_processor import (convert_image_to_webp,
                                      has_image_allowed_extention,
                                      has_image_proper_size_kb, resize_image)
from services.minio_management import MinioCRUD
from settings import settings

router = APIRouter(prefix="/projects")

ENCODERS_BY_TYPE[ObjectId] = str

class Language(StrEnum):
    EN = "en"
    RU = "ru"


class SortOrder(StrEnum):
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    POPULARITY = "popularity"


@router.get("")
async def get_projects(
    projects_crud: Annotated[ProjectsCRUD, Depends(get_projects_crud)],
    logger: Annotated[logging.Logger, Depends(get_logger_dependency)],
    lang: Language = Language.EN,
    sort: SortOrder = SortOrder.DATE_DESC,
):
    try:
        result = await projects_crud.read_all(lang=lang.value, sort=sort.value)
        if not result:
            raise HTTPException(status_code=404, detail="Projects not found")
        logger.info("Projects data fetched successfully")
        return result
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(500, detail="Internal server error")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    form_data: Annotated[
        ProjectCreateForm, Depends(ProjectCreateForm.as_form)
    ],
    projects_crud: Annotated[ProjectsCRUD, Depends(get_projects_crud)],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[logging.Logger, Depends(get_logger_dependency)],
    image: UploadFile = File(description="Project image"),
):
    try:
        if not await has_image_allowed_extention(image):
            raise HTTPException(400, "Invalid image format")
        if not await has_image_proper_size_kb(
            image, settings.PROJECT_MAX_IMAGE_SIZE_KB
        ):
            raise HTTPException(400, "Image size exceeds limit")

        image_data = await image.read()
        await image.seek(0)
        raw_image_bytes = image_data
        thumb_image_resized = await resize_image(
            image,
            settings.PROJECTS_IMAGE_THUMB_OUTPUT_WIDTH,
            settings.PROJECTS_IMAGE_THUMB_OUTPUT_HEIGHT,
            is_gif=True
        )
        thumb_image, thumb_image_filename = await convert_image_to_webp(
            thumb_image_resized
        )

        # Save images in MinIO
        raw_image_url = await minio_crud.upload_file(
            settings.PROJECTS_BUCKET_NAME, thumb_image_filename, raw_image_bytes
        )
        thumb_image_url = await minio_crud.upload_file(
            settings.PROJECTS_BUCKET_NAME,
            f"thumbnail/{thumb_image_filename}",
            thumb_image,
        )

        project_data = {
            "title": {"en": form_data.title_en, "ru": form_data.title_ru},
            "description": {
                "en": form_data.description_en,
                "ru": form_data.description_ru,
            },
            "thumbnail": thumb_image_url,
            "image": raw_image_url,
            "link": str(form_data.link),
            "date": form_data.date,
            "popularity": 0,
        }

        result = await projects_crud.create(project_data)
        return f"Project created with _id={result}"

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(500, "Internal server error")
