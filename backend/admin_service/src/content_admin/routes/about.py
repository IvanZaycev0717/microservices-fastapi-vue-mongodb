import logging
from typing import Annotated

import minio
from bson import ObjectId
from fastapi import (APIRouter, Depends, File, Form, HTTPException, Query,
                     UploadFile, status)
from pydantic import ValidationError

from content_admin.crud.about import AboutCRUD
from content_admin.dependencies import (get_about_crud, get_logger_factory,
                                        get_minio_crud)
from content_admin.models.about import (AboutCreateForm, AboutFullResponse,
                                        AboutTranslatedResponse,
                                        AboutUpdateForm, CreateAboutRequest)
from services.image_processor import (convert_image_to_webp,
                                      has_image_allowed_extention,
                                      has_image_proper_size_kb, resize_image)
from services.minio_management import MinioCRUD
from services.utils import extract_bucket_and_object_from_url
from settings import settings

router = APIRouter(prefix="/about")


@router.get(
    "", response_model=list[AboutFullResponse] | list[AboutTranslatedResponse]
)
async def get_about_content(
    about_crud: Annotated[AboutCRUD, Depends(get_about_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_ABOUT_NAME)),
    ],
    lang: Annotated[str | None, Query()] = None,
):
    """Retrieves about content from database with optional language filtering.

    Returns full content with all languages if no lang parameter provided,
    or translated content for specific language if lang parameter is specified.

    Args:
        about_crud: Dependency injection for AboutCRUD database operations.
        logger: Dependency injection for logging instance.
        lang: Optional language code to filter content (e.g., 'en', 'ru').

    Returns:
        list[AboutFullResponse] | list[AboutTranslatedResponse]:
            List of about content items. Returns full responses if no language
            specified, or translated responses for specific language.

    Raises:
        HTTPException: 404 if no content found, 500 on database error.
    """
    try:
        result = await about_crud.read_all(lang)
        if not result:
            raise HTTPException(
                status_code=404, detail="About content not found"
            )
        logger.info("About collection fetched successfully")
        return result
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching about content",
        )


@router.get(
    "/{document_id}",
    response_model=AboutFullResponse | AboutTranslatedResponse,
)
async def get_about_content_by_id(
    document_id: str,
    about_crud: Annotated[AboutCRUD, Depends(get_about_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_ABOUT_NAME)),
    ],
    lang: Annotated[str | None, Query()] = None,
):
    """Get specific about
    content document by ID with optional language filtering.

    Args:
        document_id: MongoDB ObjectId of the document to retrieve.
        lang: Optional language code ('en' or 'ru') for translated response.

    Returns:
        AboutFullResponse if no language specified,
        AboutTranslatedResponse otherwise.

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

    except HTTPException:
        raise

    except ValueError as e:
        logger.exception(f"Invalid document ID format: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format",
        )
    except Exception as e:
        logger.exception(
            f"Database error fetching document {document_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching about content",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_about_content(
    form_data: Annotated[AboutCreateForm, Depends(AboutCreateForm.as_form)],
    about_crud: Annotated[AboutCRUD, Depends(get_about_crud)],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_ABOUT_NAME)),
    ],
    image: UploadFile = File(description="Изображение для загрузки"),
):
    """Creates new about content entry with image upload and translations.

    Processes multipart form data containing image file
    and text fields in multiple languages.
    Validates image format and size,
    converts to WEBP format, uploads to MinIO storage,
    and creates database entry with structured translations.

    Args:
        form_data: Form data
        containing title and description in multiple languages.
        about_crud: Dependency injection for AboutCRUD database operations.
        minio_crud: Dependency injection for MinIO file storage operations.
        logger: Dependency injection for logging instance.
        image: Image file to upload with validation for format and size.

    Returns:
        str: Success message containing ID of created document.

    Raises:
        HTTPException:400 for invalid image format or size,
                      422 for validation errors,
                      500 for MinIO upload failures or unexpected errors.
    """
    try:
        if not await has_image_allowed_extention(image):
            error_message = "Image invalid format"
            logger.exception(error_message)
            raise HTTPException(400, error_message)
        if not await has_image_proper_size_kb(
            image, settings.ABOUT_MAX_IMAGE_SIZE_KB
        ):
            error_message = "Image size exceeds 500KB"
            logger.exception(error_message)
            raise HTTPException(400, error_message)

        resized_image = await resize_image(
            image,
            settings.ABOUT_IMAGE_OUTPUT_WIDTH,
            settings.ABOUT_IMAGE_OUTPUT_HEIGHT,
        )
        webp_image, filename = await convert_image_to_webp(resized_image)

        bucket_name = settings.ABOUT_BUCKET_NAME
        image_url = await minio_crud.upload_file(
            bucket_name, filename, webp_image
        )

        logger.info(f"Image uploaded to MinIO: {image_url}")

        data = CreateAboutRequest(
            image_url=image_url,
            translations={
                "en": {
                    "title": form_data.title_en,
                    "description": form_data.description_en,
                },
                "ru": {
                    "title": form_data.title_ru,
                    "description": form_data.description_ru,
                },
            },
        )

        result = await about_crud.create(data.model_dump(exclude_none=True))
        logger.info(f"Document created with _id={result}")
        return f"Document created with _id={result}"

    except HTTPException:
        raise

    except ValidationError as e:
        logger.exception(f"Validation error: {e}")
        raise HTTPException(422, detail=e.errors())

    except minio.error.S3Error as e:
        logger.exception(f"MinIO error: {e}")
        raise HTTPException(500, detail="Failed to upload image to storage")

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(500, detail="Internal server error")


@router.patch("/{document_id}/image", status_code=status.HTTP_200_OK)
async def update_about_image(
    document_id: str,
    image: Annotated[
        UploadFile, File(description="Новое изображение для замены")
    ],
    about_crud: Annotated[AboutCRUD, Depends(get_about_crud)],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_ABOUT_NAME)),
    ],
):
    """Updates the image for an existing about content document.

    Replaces the current image with a new uploaded image.
    Validates document existence,
    processes image (validation, resizing, WEBP conversion),
    uploads to MinIO storage,
    and deletes the old image from storage.

    Args:
        document_id: MongoDB ObjectId of the document to update.
        image: New image file to replace the existing one.
        about_crud: Dependency injection for AboutCRUD database operations.
        minio_crud: Dependency injection for MinIO file storage operations.
        logger: Dependency injection for logging instance.

    Returns:
        dict: Success message and URL of the new image.

    Raises:
        HTTPException: 400 for invalid document ID or image validation errors,
                      404 if document not found, 500 for unexpected errors.
    """
    try:
        if not ObjectId.is_valid(document_id):
            raise ValueError(f"Invalid ObjectId format: {document_id}")
        current_document = await about_crud.read_one(document_id)
        if not current_document:
            raise HTTPException(status_code=404, detail="Document not found")

        if not await has_image_allowed_extention(image):
            raise HTTPException(400, detail="Invalid image format")
        if not await has_image_proper_size_kb(
            image, settings.ABOUT_MAX_IMAGE_SIZE_KB
        ):
            raise HTTPException(400, detail="Image size exceeds limit")

        resized_image = await resize_image(
            image,
            settings.ABOUT_IMAGE_OUTPUT_WIDTH,
            settings.ABOUT_IMAGE_OUTPUT_HEIGHT,
        )
        webp_image, filename = await convert_image_to_webp(resized_image)

        bucket_name = settings.ABOUT_BUCKET_NAME
        new_image_url = await minio_crud.upload_file(
            bucket_name, filename, webp_image
        )

        old_image_url = current_document["image_url"]
        old_bucket, old_object = extract_bucket_and_object_from_url(
            old_image_url
        )
        await minio_crud.delete_file(old_bucket, old_object)

        update_data = {"image_url": new_image_url}
        await about_crud.update(document_id, update_data)

        logger.info(f"Image updated for document {document_id}")
        return {
            "message": "Image updated successfully",
            "image_url": new_image_url,
        }

    except ValueError as e:
        logger.exception(f"Invalid document ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Error updating image: {e}")
        raise HTTPException(500, detail="Failed to update image")


@router.patch("/{document_id}", status_code=status.HTTP_200_OK)
async def update_about_content(
    document_id: str,
    form_data: Annotated[AboutUpdateForm, Form()],
    about_crud: Annotated[AboutCRUD, Depends(get_about_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_ABOUT_NAME)),
    ],
):
    """Updates translations for an existing about content document.

    Modifies title and description fields for English and Russian translations.
    If any field is not provided in the form data,
    retains the existing value from the document.
    Validates document existence and ObjectId format before performing update.

    Args:
        document_id: MongoDB ObjectId of the document to update.
        form_data: Form data containing
        optional title and description fields for both languages.
        about_crud: Dependency injection for AboutCRUD database operations.
        logger: Dependency injection for logging instance.

    Returns:
        dict: Success message and ID of the updated document.

    Raises:
        HTTPException: 400 for invalid document ID or empty update data,
                      404 if document not found, 500 for unexpected errors.
    """
    try:
        if not ObjectId.is_valid(document_id):
            raise ValueError(f"Invalid ObjectId format: {document_id}")

        document = await about_crud.read_one(document_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )

        if not form_data.title_en:
            form_data.title_en = document["translations"]["en"]["title"]

        if not form_data.description_en:
            form_data.description_en = document["translations"]["en"][
                "description"
            ]

        if not form_data.title_ru:
            form_data.title_ru = document["translations"]["ru"]["title"]

        if not form_data.description_ru:
            form_data.description_ru = document["translations"]["ru"]["title"]

        update_data = {
            "translations": {
                "en": {
                    "title": form_data.title_en,
                    "description": form_data.description_en,
                },
                "ru": {
                    "title": form_data.title_ru,
                    "description": form_data.description_ru,
                },
            }
        }

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for update",
            )

        result = await about_crud.update(document_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )

        logger.info(f"Document {document_id} updated successfully")
        return {
            "message": "Document updated successfully",
            "document_id": document_id,
        }

    except ValueError as e:
        logger.exception(f"Invalid document ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during update",
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_about_content(
    document_id: str,
    about_crud: Annotated[AboutCRUD, Depends(get_about_crud)],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_ABOUT_NAME)),
    ],
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
        if not ObjectId.is_valid(document_id):
            raise ValueError(f"Invalid ObjectId format: {document_id}")
        document = await about_crud.read_one(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )
        image_url = document["image_url"]
        bucket_name, object_name = extract_bucket_and_object_from_url(
            image_url
        )

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
