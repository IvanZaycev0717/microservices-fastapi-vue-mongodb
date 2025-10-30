import io

from fastapi import HTTPException, status
from pdf2image import convert_from_bytes

from services.logger import get_logger
from settings import settings

logger = get_logger("pdf-processor")


async def validate_pdf_size(pdf_file: bytes, max_size_kb: int) -> None:
    """Validate PDF file size.

    Args:
        pdf_file: PDF file bytes
        max_size_kb: Maximum allowed size in KB

    Raises:
        HTTPException: If PDF exceeds size limit
    """
    pdf_size_kb = len(pdf_file) / 1024
    if pdf_size_kb > max_size_kb:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"PDF size {pdf_size_kb:.1f}KB exceeds {max_size_kb}KB limit",
        )


async def convert_pdf_to_image(pdf_file: bytes, max_size_kb: int) -> bytes:
    """Convert first page of PDF to image bytes.

    Args:
        pdf_file: PDF file bytes
        max_size_kb: Maximum allowed PDF size in KB

    Returns:
        bytes: Image bytes in WEBP format

    Raises:
        HTTPException: If PDF is too large or conversion fails
    """
    try:
        await validate_pdf_size(pdf_file, max_size_kb)

        images = convert_from_bytes(
            pdf_file,
            first_page=settings.PDF_FIRST_PAGE,
            last_page=settings.PDF_LAST_PAGE,
            dpi=settings.PDF_DPI,
            fmt=settings.PDF_OUTPUT_IMAGE_FORMAT,
            thread_count=settings.PDF_THREAD_COUNT,
        )

        if not images:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Failed to convert PDF to image"
            )

        # Convert PIL Image to bytes
        img_buffer = io.BytesIO()
        images[0].save(img_buffer, format="WEBP", quality=95)
        img_buffer.seek(0)

        return img_buffer.getvalue()

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"PDF conversion error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to process PDF file"
        )
