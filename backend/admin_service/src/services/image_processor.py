import io
import uuid
from pathlib import Path
from typing import NamedTuple

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from services.logger import get_logger

logger = get_logger("image-processor")

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
    """Resize and process image for optimal display.

    Args:
        image (UploadFile): Image file to process.
        width (int): Target width for resizing.
        height (int): Target height for resizing.
        is_gif (bool): Whether the image is a GIF format.

    Returns:
        UploadFile: Processed image in WEBP format.

    Raises:
        HTTPException: If image format is invalid or cannot be processed.
    """
    image_data = await image.read()
    await image.seek(0)

    try:
        if is_gif:
            with Image.open(io.BytesIO(image_data)) as img:
                img.seek(0)
                frame = img.copy()
                img = frame.convert("RGB")
        else:
            img = Image.open(io.BytesIO(image_data))

        orig_width, orig_height = img.size

        if width == height:
            min_dimension = min(orig_width, orig_height)
            left = (orig_width - min_dimension) // 2
            top = (orig_height - min_dimension) // 2
            img_cropped = img.crop(
                (left, top, left + min_dimension, top + min_dimension)
            )

            img_resized = img_cropped.resize(
                (width, height), Image.Resampling.LANCZOS
            )

            output_buffer = io.BytesIO()
            img_resized.save(output_buffer, format="WEBP")

        else:
            is_vertical = orig_height > orig_width
            if is_vertical:
                target_width, target_height = width, height
            else:
                target_width, target_height = height, width

            width_ratio = target_width / orig_width
            height_ratio = target_height / orig_height
            ratio = min(width_ratio, height_ratio)

            new_width = int(orig_width * ratio)
            new_height = int(orig_height * ratio)

            img_resized = img.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )

            background = Image.new(
                "RGB", (target_width, target_height), (255, 255, 255)
            )

            x = (target_width - new_width) // 2
            y = (target_height - new_height) // 2
            background.paste(img_resized, (x, y))

            output_buffer = io.BytesIO()
            background.save(output_buffer, format="WEBP")

        output_buffer.seek(0)
        return UploadFile(
            filename=image.filename.replace(".gif", ".webp"),
            file=output_buffer,
            headers={"content-type": "image/webp"},
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
