import io
import logging
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from typing import Annotated, List, Dict, Any
from content_admin.dependencies import (
    SortOrder,
    get_logger_factory,
    get_minio_crud,
)
from content_admin.crud.certificates import CertificatesCRUD
from content_admin.dependencies import get_certificates_crud
from settings import settings
from fastapi import status

from content_admin.models.certificates import CertificateCreateForm
from services.minio_management import MinioCRUD
from services.image_processor import (
    convert_image_to_webp,
    has_image_allowed_extention,
    has_image_proper_size_kb,
    resize_image,
)
from services.pdf_processor import convert_pdf_to_image

router = APIRouter(prefix="/certificates")


@router.get("")
async def get_certificates(
    logger: Annotated[
        logging.Logger,
        Depends(
            get_logger_factory(settings.CONTENT_SERVICE_CERTIFICATES_NAME)
        ),
    ],
    certificates_crud: Annotated[
        CertificatesCRUD, Depends(get_certificates_crud)
    ],
    sort: SortOrder = SortOrder.DATE_DESC,
) -> List[Dict[str, Any]]:
    try:
        results = await certificates_crud.read_all(sort=sort.value)
        if not results:
            raise HTTPException(
                status_code=404, detail="Certificates not found"
            )
        logger.info("All certificates successfully fetched")
        return results
    except HTTPException as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(500, detail="Internal server error")


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
        Depends(
            get_logger_factory(settings.CONTENT_SERVICE_CERTIFICATES_NAME)
        ),
    ],
    file: UploadFile = File(description="Certificate PDF or image"),
):
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
                raise HTTPException(400, "Invalid image format")
            if not await has_image_proper_size_kb(
                file, settings.CERTIFICATE_MAX_IMAGE_SIZE_KB
            ):
                raise HTTPException(400, "Image size exceeds limit")
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
        raise HTTPException(500, "Internal server error")
