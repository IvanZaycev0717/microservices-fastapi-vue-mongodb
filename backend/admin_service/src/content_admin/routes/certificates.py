import io
import logging
from typing import Annotated, Any, Dict, List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    UploadFile,
    status,
)

from content_admin.crud.certificates import CertificatesCRUD
from content_admin.dependencies import (
    SortOrder,
    get_certificates_crud,
    get_logger_factory,
    get_minio_crud,
)
from content_admin.models.certificates import CertificateCreateForm
from services.image_processor import (
    convert_image_to_webp,
    has_image_allowed_extention,
    has_image_proper_size_kb,
    resize_image,
)
from services.minio_management import MinioCRUD
from services.pdf_processor import convert_pdf_to_image
from services.utils import extract_bucket_and_object_from_url
from settings import settings

router = APIRouter(prefix="/certificates")


@router.get("")
async def get_certificates(
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_ADMIN_CERTIFICATES_NAME)),
    ],
    certificates_crud: Annotated[
        CertificatesCRUD, Depends(get_certificates_crud)
    ],
    sort: SortOrder = SortOrder.DATE_DESC,
) -> List[Dict[str, Any]]:
    """Retrieve all certificates with sorting option.

    Args:
        logger: Injected logger instance for certificates admin.
        certificates_crud: Injected certificates CRUD dependency.
        sort: Sorting order for certificates.

    Returns:
        List[Dict[str, Any]]: List of certificate data.

    Raises:
        HTTPException: If certificates not found or internal error occurs.
    """
    try:
        results = await certificates_crud.read_all(sort=sort.value)
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificates not found",
            )
        logger.info("All certificates successfully fetched")
        return results
    except HTTPException as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_certificate(
    form_data: Annotated[
        CertificateCreateForm, Depends(CertificateCreateForm.as_form)
    ],
    certificates_crud: Annotated[
        CertificatesCRUD, Depends(get_certificates_crud)
    ],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_ADMIN_CERTIFICATES_NAME)),
    ],
    file: Annotated[UploadFile, File(description="Certificate PDF or image")],
):
    """Create a new certificate with image processing and storage.

    Args:
        form_data: Form data containing certificate information.
        certificates_crud: Injected certificates CRUD dependency.
        minio_crud: Injected MinIO CRUD dependency for file storage.
        logger: Injected logger instance for certificates admin.
        file: Uploaded certificate file (PDF or image).

    Returns:
        str: Success message with created certificate ID.

    Raises:
        HTTPException: If file validation fails or internal error occurs.
    """
    try:
        file_bytes = await file.read()

        is_pdf = file_bytes.startswith(b"%PDF-")

        if is_pdf:
            image_data = await convert_pdf_to_image(
                file_bytes, settings.CERTIFICATE_MAX_PDF_SIZE_KB
            )

            pdf_image = UploadFile(
                filename=file.filename.replace(".pdf", ".webp"),
                file=io.BytesIO(image_data),
            )
            processing_file = pdf_image

        else:
            await file.seek(0)
            if not await has_image_allowed_extention(file):
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Invalid image format"
                )
            if not await has_image_proper_size_kb(
                file, settings.CERTIFICATE_MAX_IMAGE_SIZE_KB
            ):
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Image size exceeds limit"
                )
            processing_file = file

        main_image_resized = await resize_image(
            processing_file,
            settings.CERTIFICATES_IMAGE_OUTPUT_WIDTH,
            settings.CERTIFICATES_IMAGE_OUTPUT_HEIGHT,
        )
        main_image, main_image_filename = await convert_image_to_webp(
            main_image_resized
        )

        thumb_image_resized = await resize_image(
            processing_file,
            settings.CERTIFICATES_IMAGE_THUMB_OUTPUT_WIDTH,
            settings.CERTIFICATES_IMAGE_THUMB_OUTPUT_HEIGHT,
        )
        thumb_image, _ = await convert_image_to_webp(thumb_image_resized)

        main_image_url = await minio_crud.upload_file(
            settings.CERTIFICATES_BUCKET_NAME, main_image_filename, main_image
        )
        thumb_image_url = await minio_crud.upload_file(
            settings.CERTIFICATES_BUCKET_NAME,
            f"thumbnail/{main_image_filename}",
            thumb_image,
        )

        alt_text = f"certificate_{main_image_filename.replace('.webp', '')}"

        certificate_data = {
            "src": str(main_image_url),
            "thumb": str(thumb_image_url),
            "alt": alt_text,
            "date": form_data.date,
            "popularity": form_data.popularity,
        }

        result = await certificates_crud.create(certificate_data)
        return f"Certificate created with _id={result}"

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"
        )


@router.get("/{certificate_id}")
async def get_certificate_by_id(
    certificate_id: Annotated[
        str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)
    ],
    certificates_crud: Annotated[
        CertificatesCRUD, Depends(get_certificates_crud)
    ],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_ADMIN_CERTIFICATES_NAME)),
    ],
):
    """Retrieve a specific certificate by ID.

    Args:
        certificate_id: ID of the certificate to retrieve.
        certificates_crud: Injected certificates CRUD dependency.
        logger: Injected logger instance for certificates admin.

    Returns:
        dict: Certificate data if found.

    Raises:
        HTTPException: If certificate not found or internal error occurs.
    """
    try:
        certificate = await certificates_crud.read_one_by_id(certificate_id)
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certificate with id {certificate_id} not found",
            )

        logger.info(f"Certificate {certificate_id} fetched successfully")
        return certificate

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching certificate",
        )


@router.patch("/{certificate_id}/image")
async def update_certificate_image(
    certificate_id: Annotated[
        str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)
    ],
    certificates_crud: Annotated[
        CertificatesCRUD, Depends(get_certificates_crud)
    ],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_ADMIN_CERTIFICATES_NAME)),
    ],
    file: Annotated[UploadFile, File(description="New certificate image")],
):
    """Update certificate image with processing and storage.

    Args:
        certificate_id: ID of the certificate to update.
        certificates_crud: Injected certificates CRUD dependency.
        minio_crud: Injected MinIO CRUD dependency for file storage.
        logger: Injected logger instance for certificates admin.
        file: New certificate image file to upload.

    Returns:
        str: Success message.

    Raises:
        HTTPException: If certificate not found, file validation fails, or internal error occurs.
    """
    try:
        current_cert = await certificates_crud.read_one_by_id(certificate_id)
        if not current_cert:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Certificate with id {certificate_id} not found",
            )

        file_bytes = await file.read()
        is_pdf = file_bytes.startswith(b"%PDF-")

        if is_pdf:
            image_data = await convert_pdf_to_image(
                file_bytes, settings.CERTIFICATE_MAX_PDF_SIZE_KB
            )
            processing_file = UploadFile(
                filename=file.filename.replace(".pdf", ".webp"),
                file=io.BytesIO(image_data),
            )
        else:
            await file.seek(0)
            if not await has_image_allowed_extention(file):
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Invalid image format"
                )
            if not await has_image_proper_size_kb(
                file, settings.CERTIFICATE_MAX_IMAGE_SIZE_KB
            ):
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "Image size exceeds limit"
                )
            processing_file = file

        main_image_resized = await resize_image(
            processing_file,
            settings.CERTIFICATES_IMAGE_OUTPUT_WIDTH,
            settings.CERTIFICATES_IMAGE_OUTPUT_HEIGHT,
        )
        main_image, main_image_filename = await convert_image_to_webp(
            main_image_resized
        )

        thumb_image_resized = await resize_image(
            processing_file,
            settings.CERTIFICATES_IMAGE_THUMB_OUTPUT_WIDTH,
            settings.CERTIFICATES_IMAGE_THUMB_OUTPUT_HEIGHT,
        )
        thumb_image, _ = await convert_image_to_webp(thumb_image_resized)

        main_image_url = await minio_crud.upload_file(
            settings.CERTIFICATES_BUCKET_NAME,
            main_image_filename,
            main_image,
        )
        thumb_image_url = await minio_crud.upload_file(
            settings.CERTIFICATES_BUCKET_NAME,
            f"thumbnail/{main_image_filename}",
            thumb_image,
        )

        old_src = current_cert["src"]
        old_thumb = current_cert["thumb"]

        try:
            bucket, obj_name = extract_bucket_and_object_from_url(old_src)
            await minio_crud.delete_file(bucket, obj_name)
            bucket, obj_name = extract_bucket_and_object_from_url(old_thumb)
            await minio_crud.delete_file(bucket, obj_name)
        except Exception as e:
            logger.warning(f"Failed to delete old images: {e}")

        update_data = {
            "src": main_image_url,
            "thumb": thumb_image_url,
            "alt": f"certificate_{main_image_filename.replace('.webp', '')}",
        }

        updated = await certificates_crud.update(certificate_id, update_data)
        if not updated:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to update certificate image",
            )

        logger.info(f"Certificate image updated: {certificate_id}")
        return "Certificate image updated successfully"

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"
        )


@router.patch("/{certificate_id}")
async def update_certificate_popularity(
    certificates_crud: Annotated[
        CertificatesCRUD, Depends(get_certificates_crud)
    ],
    certificate_id: Annotated[
        str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)
    ],
    popularity: int = Form(
        ge=settings.MIN_POPULARITY_BOUNDARY,
        le=settings.MAX_POPULARITY_BOUNDARY,
        description="Popularity value (0-1000)",
        json_schema_extra={"example": 5},
    ),
    logger: logging.Logger = Depends(
        get_logger_factory(settings.CONTENT_ADMIN_CERTIFICATES_NAME)
    ),
):
    """Update certificate popularity value.

    Args:
        certificates_crud: Injected certificates CRUD dependency.
        certificate_id: ID of the certificate to update.
        popularity: New popularity value within defined boundaries.
        logger: Injected logger instance for certificates admin.

    Returns:
        str: Success message.

    Raises:
        HTTPException: If certificate not found or internal error occurs.
    """
    try:
        current_cert = await certificates_crud.read_one_by_id(certificate_id)
        if not current_cert:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Certificate with id {certificate_id} not found",
            )

        updated = await certificates_crud.update(
            certificate_id, {"popularity": popularity}
        )
        if not updated:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to update certificate popularity",
            )

        return "Certificate popularity updated successfully"

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"
        )


@router.delete("/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certificate(
    certificate_id: Annotated[
        str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)
    ],
    certificates_crud: Annotated[
        CertificatesCRUD, Depends(get_certificates_crud)
    ],
    minio_crud: Annotated[MinioCRUD, Depends(get_minio_crud)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_ADMIN_CERTIFICATES_NAME)),
    ],
):
    """Delete certificate and associated images from storage.

    Args:
        certificate_id: ID of the certificate to delete.
        certificates_crud: Injected certificates CRUD dependency.
        minio_crud: Injected MinIO CRUD dependency for file storage.
        logger: Injected logger instance for certificates admin.

    Raises:
        HTTPException: If certificate not found or internal error occurs.
    """
    try:
        certificate = await certificates_crud.read_one_by_id(certificate_id)
        if not certificate:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Certificate with id {certificate_id} not found",
            )

        try:
            bucket, object_name = extract_bucket_and_object_from_url(
                certificate["src"]
            )
            await minio_crud.delete_file(bucket, object_name)

            bucket, object_name = extract_bucket_and_object_from_url(
                certificate["thumb"]
            )
            await minio_crud.delete_file(bucket, object_name)

            logger.info(f"Deleted images for certificate {certificate_id}")

        except ValueError as e:
            logger.warning(f"Invalid MinIO URL format: {e}")
        except Exception as e:
            logger.warning(f"Failed to delete images from storage: {e}")

        deleted = await certificates_crud.delete(certificate_id)
        if not deleted:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to delete certificate from database",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"
        )
