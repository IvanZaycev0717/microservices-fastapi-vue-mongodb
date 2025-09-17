import logging
from typing import Annotated
from urllib.parse import urlparse

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from content_admin.crud.projects import ProjectsCRUD
from content_admin.dependencies import (
    get_logger_factory,
    get_minio_crud,
    get_projects_crud,
)
from content_admin.models.projects import ProjectCreateForm, ProjectUpdateRequest
from services.image_processor import (
    convert_image_to_webp,
    has_image_allowed_extention,
    has_image_proper_size_kb,
    resize_image,
)
from services.minio_management import MinioCRUD
from services.utils import extract_bucket_and_object_from_url
from settings import settings
from content_admin.dependencies import Language, SortOrder

router = APIRouter(prefix="/projects")


@router.get("")
async def get_projects(
    projects_crud: Annotated[ProjectsCRUD, Depends(get_projects_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
    lang: Language = Language.EACH,
    sort: SortOrder = SortOrder.DATE_DESC,
):
    try:
        result = await projects_crud.read_all(lang=lang.value, sort=sort.value)
        if not result:
            raise HTTPException(status_code=404, detail="Projects not found")
        logger.info("Projects data fetched successfully")
        return result
    except HTTPException as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(500, detail="Internal server error")


@router.get("/{document_id}")
async def get_project_by_id(
    document_id: str,
    projects_crud: Annotated[ProjectsCRUD, Depends(get_projects_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
    lang: Language = Language.EACH,
):
    try:
        result = await projects_crud.read_by_id(document_id, lang.value)
        if not result:
            raise HTTPException(status_code=404, detail="Project not found")
        logger.info(f"Project {document_id} fetched successfully")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(500, detail="Internal server error")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    form_data: Annotated[ProjectCreateForm, Depends(ProjectCreateForm.as_form)],
    projects_crud: Annotated[ProjectsCRUD, Depends(get_projects_crud)],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
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
            is_gif=True,
        )
        thumb_image, thumb_image_filename = await convert_image_to_webp(
            thumb_image_resized
        )

        raw_image_filename = thumb_image_filename.replace(".webp", ".gif")

        # Save images in MinIO
        raw_image_url = await minio_crud.upload_file(
            settings.PROJECTS_BUCKET_NAME, raw_image_filename, raw_image_bytes
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
            "popularity": form_data.popularity,
        }

        result = await projects_crud.create(project_data)
        return f"Project created with _id={result}"
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(500, "Internal server error")


@router.patch("/{document_id}/image")
async def update_project_image(
    document_id: str,
    projects_crud: Annotated[ProjectsCRUD, Depends(get_projects_crud)],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
    image: UploadFile = File(description="New project image"),
):
    """Update project image and thumbnail in MinIO and database."""
    try:
        project = await projects_crud.read_by_id(document_id, "en")
        if not project:
            raise HTTPException(404, "Project not found")

        if not await has_image_allowed_extention(image):
            raise HTTPException(400, "Invalid image format")
        if not await has_image_proper_size_kb(
            image, settings.PROJECT_MAX_IMAGE_SIZE_KB
        ):
            raise HTTPException(400, "Image size exceeds limit")

        image_data = await image.read()
        await image.seek(0)
        thumb_image_resized = await resize_image(
            image,
            settings.PROJECTS_IMAGE_THUMB_OUTPUT_WIDTH,
            settings.PROJECTS_IMAGE_THUMB_OUTPUT_HEIGHT,
            is_gif=True,
        )
        thumb_image, thumb_image_filename = await convert_image_to_webp(
            thumb_image_resized
        )

        old_image_url = project["image"]
        old_thumb_url = project["thumbnail"]

        def parse_minio_url(url):
            parsed = urlparse(url)
            bucket = parsed.path.split("/")[1]
            object_name = "/".join(parsed.path.split("/")[2:])
            return bucket, object_name

        try:
            bucket, object_name = parse_minio_url(old_image_url)
            await minio_crud.delete_file(bucket, object_name)

            bucket, object_name = parse_minio_url(old_thumb_url)
            await minio_crud.delete_file(bucket, object_name)
        except Exception as e:
            logger.warning(f"Failed to delete old images: {e}")

        raw_image_filename = thumb_image_filename.replace(".webp", ".gif")
        raw_image_url = await minio_crud.upload_file(
            settings.PROJECTS_BUCKET_NAME, raw_image_filename, image_data
        )
        thumb_image_url = await minio_crud.upload_file(
            settings.PROJECTS_BUCKET_NAME,
            f"thumbnail/{thumb_image_filename}",
            thumb_image,
        )

        await projects_crud.update(
            document_id, {"image": raw_image_url, "thumbnail": thumb_image_url}
        )

        return "Project image updated successfully"

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(500, "Internal server error")


@router.patch("/{document_id}")
async def update_project(
    document_id: str,
    request: Request,
    form_data: Annotated[ProjectUpdateRequest, Form()],
    projects_crud: Annotated[ProjectsCRUD, Depends(get_projects_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
):
    try:
        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" not in content_type:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only application/x-www-form-urlencoded data is supported"
            )
        if not ObjectId.is_valid(document_id):
            raise HTTPException(404, f"Invalid Document ID': {document_id}")

        document = await projects_crud.read_by_id(document_id, "all")
        if not document:
            raise HTTPException(404, f"Document with id {document_id} not found")

        update_data = {"title": {}, "description": {}}

        if form_data.title_en is None or form_data.title_en == "":
            form_data.title_en = document["title"].get("en", "")
        if form_data.title_ru is None or form_data.title_ru == "":
            form_data.title_ru = document["title"].get("ru", "")
        if form_data.description_en is None or form_data.description_en == "":
            form_data.description_en = document["description"].get("en", "")
        if form_data.description_ru is None or form_data.description_ru == "":
            form_data.description_ru = document["description"].get("ru", "")

        if not form_data.link:
            form_data.link = str(document["link"])

        update_data["title"]["en"] = form_data.title_en
        update_data["description"]["en"] = form_data.description_en

        update_data["title"]["ru"] = form_data.title_ru
        update_data["description"]["ru"] = form_data.description_ru

        update_data["link"] = str(form_data.link)
        update_data["popularity"] = form_data.popularity

        await projects_crud.update(document_id, update_data)

        logger.info(f"Project {document_id} updated successfully")
        return {"message": "Project updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(500, "Internal server error")


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    document_id: str,
    projects_crud: Annotated[ProjectsCRUD, Depends(get_projects_crud)],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
):
    try:
        if not ObjectId.is_valid(document_id):
            raise HTTPException(400, "Invalid document ID format")
        
        document = await projects_crud.read_by_id(document_id, Language.EN)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )

        image_url = str(document["image"])
        thumb_image_url = str(document["thumbnail"])

        _, image_object_name = extract_bucket_and_object_from_url(image_url)
        _, thumb_object_name = extract_bucket_and_object_from_url(thumb_image_url)

        await minio_crud.delete_file(settings.PROJECTS_BUCKET_NAME, image_object_name)
        await minio_crud.delete_file(settings.PROJECTS_BUCKET_NAME, thumb_object_name)
        logger.info(
            f"Deleted image from MinIO: {image_object_name, thumb_object_name} from bucket {settings.PROJECTS_BUCKET_NAME}"
        )
        deleted = await projects_crud.delete(document_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found after image deletion",
            )
    except ValueError as e:
        logger.exception(f"Invalid document ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting document or image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document and associated image",
        )
