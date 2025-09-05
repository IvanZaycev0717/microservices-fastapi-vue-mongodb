import logging
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
import minio
from pydantic import ValidationError

from content_admin.crud.about import AboutCRUD
from content_admin.dependencies import (
    get_about_crud,
    get_logger_dependency,
    get_minio_crud,
)
from content_admin.models.about import (
    AboutFullResponse,
    AboutTranslatedResponse,
    CreateAboutRequest,
)
from services.image_processor import (
    convert_image_to_webp,
    has_image_allowed_extention,
    has_image_proper_size_kb,
    resize_image,
)
from services.utils import extract_bucket_and_object_from_url
from settings import settings
from services.minio_management import MinioCRUD

router = APIRouter(prefix="/about")


@router.get("", response_model=list[AboutFullResponse] | list[AboutTranslatedResponse])
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


@router.get(
    "/{document_id}", response_model=AboutFullResponse | AboutTranslatedResponse
)
async def get_about_content_by_id(
    document_id: str,
    lang: Optional[str] = Query(None),
    about_crud: AboutCRUD = Depends(get_about_crud),
    logger: logging.Logger = Depends(get_logger_dependency),
):
    """Get specific about content document by ID with optional language filtering.

    Args:
        document_id: MongoDB ObjectId of the document to retrieve.
        lang: Optional language code ('en' or 'ru') for translated response.

    Returns:
        AboutFullResponse if no language specified, AboutTranslatedResponse otherwise.

    Raises:
        HTTPException 404: If document with specified ID is not found.
        HTTPException 400: If invalid document ID format provided.
        HTTPException 500: If internal server error occurs.
    """
    try:
        result = await about_crud.read_one(document_id, lang)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )
        logger.info(f"About document {document_id} fetched successfully")
        return result

    except ValueError as e:
        logger.error(f"Invalid document ID format: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format"
        )
    except Exception as e:
        logger.error(f"Database error fetching document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching about content",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
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
    minio_crud: MinioCRUD = Depends(get_minio_crud),
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
        webp_image, filename = await convert_image_to_webp(resized_image)

        bucket_name = settings.ABOUT_STR
        image_url = await minio_crud.upload_file(bucket_name, filename, webp_image)

        logger.info(f"Image uploaded to MinIO: {image_url}")

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

    except minio.error.S3Error as e:
        logger.error(f"MinIO error: {e}")
        raise HTTPException(500, detail="Failed to upload image to storage")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(500, detail="Internal server error")


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_about_content(
    document_id: str,
    about_crud: AboutCRUD = Depends(get_about_crud),
    minio_crud: MinioCRUD = Depends(get_minio_crud),
    logger: logging.Logger = Depends(get_logger_dependency),
):
    """Delete about content document by ID and associated image from MinIO.

    Args:
        document_id: MongoDB ObjectId of the document to delete.

    Raises:
        HTTPException 404: If document with specified ID is not found.
        HTTPException 400: If invalid document ID format provided.
        HTTPException 500: If internal server error occurs during deletion.
    """
    try:
        document = await about_crud.read_one(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )
        image_url = document["image_url"]
        bucket_name, object_name = extract_bucket_and_object_from_url(image_url)

        await minio_crud.delete_file(bucket_name, object_name)
        logger.info(
            f"Deleted image from MinIO: {object_name} from bucket {bucket_name}"
        )

        deleted = await about_crud.delete(document_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found after image deletion",
            )

    except ValueError as e:
        logger.error(f"Invalid document ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document or image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document and associated image",
        )
