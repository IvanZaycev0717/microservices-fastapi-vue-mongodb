import io

from fastapi import HTTPException
from pdf2image import convert_from_bytes

from services.logger import get_logger

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
            400, f"PDF size {pdf_size_kb:.1f}KB exceeds {max_size_kb}KB limit"
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
            first_page=1,
            last_page=1,
            dpi=300,
            fmt="webp",
            thread_count=4,
        )

        if not images:
            raise HTTPException(400, "Failed to convert PDF to image")

        # Convert PIL Image to bytes
        img_buffer = io.BytesIO()
        images[0].save(img_buffer, format="WEBP", quality=95)
        img_buffer.seek(0)

        return img_buffer.getvalue()

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"PDF conversion error: {e}")
        raise HTTPException(500, "Failed to process PDF file")
