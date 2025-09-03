import io
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image

from settings import settings


async def generate_image_filename(image: UploadFile) -> str:
    """Generate unique filename for uploaded image using UUID.

    Args:
        image: Uploaded file object to extract extension from.

    Returns:
        str: Unique filename in format 'uuidhex.extension'.

    Example:
        'a1b2c3d4e5f67890123456789abcdef0.jpg'
    """
    file_ext = Path(image.filename).suffix.lower()
    return f"{uuid.uuid4().hex}{file_ext}"


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


async def has_image_proper_size_kb(image: UploadFile) -> bool:
    """Check if the uploaded image size is within allowed limits.

    Args:
        image: The uploaded file object to validate.

    Returns:
        bool: True if the image size is within allowed limits, False otherwise.

    Notes:
        Reads the file content to determine size, then resets the file pointer to position 0.
        Uses MAX_IMAGE_SIZE_KB from settings to determine maximum allowed size in kilobytes.
    """
    max_size = settings.MAX_IMAGE_SIZE_KB * 1024
    content = await image.read()
    if len(content) > max_size:
        return False
    await image.seek(0)
    return True


async def resize_image(image: UploadFile) -> UploadFile:
    """Resize image to square format with dimensions from settings.

    Args:
        image: Uploaded image file that passed validation.

    Returns:
        UploadFile: Resized image file in square format.
    """
    width = settings.IMAGE_OUTPUT_WIDTH
    height = settings.IMAGE_OUTPUT_HEIGHT

    # Pillow handling
    image_data = await image.read()
    img = Image.open(io.BytesIO(image_data))

    orig_width, orig_height = img.size
    min_dimension = min(orig_width, orig_height)
    left = (orig_width - min_dimension) // 2
    top = (orig_height - min_dimension) // 2
    img_cropped = img.crop((left, top, left + min_dimension, top + min_dimension))

    # Resize to target dimensions
    img_resized = img_cropped.resize((width, height), Image.Resampling.LANCZOS)

    # Convert back to bytes
    output_buffer = io.BytesIO()
    img_format = img.format or "JPEG"
    img_resized.save(output_buffer, format=img_format)
    output_buffer.seek(0)

    return UploadFile(
        filename=image.filename,
        file=output_buffer,
        headers={"content-type": image.content_type},
    )


async def save_image_as_webp(
    image: UploadFile, filepath: str, subfolder: str, filename: str
) -> str:
    """Convert and save uploaded image as WEBP format with absolute URL.

    Args:
        image: Uploaded image file.
        filename: Generated filename for the image (without extension).

    Returns:
        str: Absolute URL to access the saved WEBP image.
    """
    import io

    from PIL import Image

    # Read and convert to WEBP
    image_data = await image.read()
    img = Image.open(io.BytesIO(image_data))

    # Save as WEBP
    filename_without_ext = Path(filename).stem
    webp_filename = f"{filename_without_ext}.webp"
    webp_path = filepath / webp_filename

    img.save(webp_path, "WEBP", quality=80)

    return f"http://localhost:8000/images/{subfolder}/{webp_filename}"
