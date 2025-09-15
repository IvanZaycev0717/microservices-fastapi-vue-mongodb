import io
import uuid
from pathlib import Path
from typing import NamedTuple

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from services.logger import get_logger

logger = get_logger("projects-crud")

from settings import settings


class WebpResult(NamedTuple):
    """Container for converted WEBP image data.

    Attributes:
        image_bytes: Binary data of the converted WEBP image.
        filename: Generated filename in format 'uuid.webp'.
    """

    image_bytes: bytes
    filename: str


async def has_image_allowed_extention(image: UploadFile) -> bool:
    """Check if the uploaded image has an allowed file extension.

    Args:
        image: The uploaded file object to validate.

    Returns:
        bool: True if the file extension is allowed, False otherwise.

    Notes:
        Resets the file pointer to position 0 after validation.
    """
    allowed_extensions = settings.ALLOWED_IMAGE_EXTENSIONS
    file_ext = Path(image.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        return False
    await image.seek(0)
    return True


async def has_image_proper_size_kb(image: UploadFile, max_size: int) -> bool:
    """Check if the uploaded image size is within allowed limits.

    Args:
        image: The uploaded file object to validate.

    Returns:
        bool: True if the image size is within allowed limits, False otherwise.

    Notes:
        Reads the file content to determine size, then resets the file pointer to position 0.
        Uses MAX_IMAGE_SIZE_KB from settings to determine maximum allowed size in kilobytes.
    """
    content = await image.read()
    if len(content) > max_size:
        return False
    await image.seek(0)
    return True


async def resize_image(
    image: UploadFile, width: int, height: int, is_gif: bool = False
) -> UploadFile:
    """Resize image to square format with dimensions from settings.

    Args:
        image: Uploaded image file that passed validation.

    Returns:
        UploadFile: Resized image file in square format.
    """
    image_data = await image.read()
    try:
        if is_gif:
            with Image.open(io.BytesIO(image_data)) as img:
                img.seek(0)
                frame = img.copy()
                img = frame.convert("RGB")
        else:
            img = Image.open(io.BytesIO(image_data))

        orig_width, orig_height = img.size
        min_dimension = min(orig_width, orig_height)
        left = (orig_width - min_dimension) // 2
        top = (orig_height - min_dimension) // 2
        img_cropped = img.crop((left, top, left + min_dimension, top + min_dimension))

        img_resized = img_cropped.resize((width, height), Image.Resampling.LANCZOS)

        output_buffer = io.BytesIO()
        img_resized.save(output_buffer, format="WEBP")
        output_buffer.seek(0)

        return UploadFile(
            filename=image.filename.replace(".gif", ".webp"),
            file=output_buffer,
            headers={"content-type": image.content_type},
        )
    except UnidentifiedImageError:
        logger.exception(f"Cannot identify image: {image.filename}")
        raise HTTPException(400, "Invalid image format")


async def convert_image_to_webp(image: UploadFile) -> WebpResult:
    """Convert uploaded image to WEBP format with UUID filename.

    Args:
        image: Uploaded image file in any supported format.

    Returns:
        tuple: WEBP image bytes and generated filename in format 'uuid.webp'.

    Example:
        (b'webp_data', 'a1b2c3d4e5f67890123456789abcdef0.webp')
    """
    image_data = await image.read()
    img = Image.open(io.BytesIO(image_data))

    if hasattr(img, "is_animated") and img.is_animated:
        img.seek(0)
        frame = img.copy()
        img = frame.convert("RGB")

    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background

    webp_buffer = io.BytesIO()
    img.save(webp_buffer, "WEBP", quality=80)

    filename = f"{uuid.uuid4().hex}.webp"
    return webp_buffer.getvalue(), filename
