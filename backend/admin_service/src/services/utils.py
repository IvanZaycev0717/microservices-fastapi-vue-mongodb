from typing import Any
from urllib.parse import urlparse

def extract_bucket_and_object_from_url(file_url: str) -> tuple[str, str]:
    """Extract bucket name and object name from MinIO file URL.

    Args:
        file_url: Full MinIO file URL (e.g. "http://localhost:9000/bucket/path/to/file.webp")

    Returns:
        tuple: (bucket_name, object_name) extracted from the URL

    Raises:
        ValueError: If URL format is invalid or cannot be parsed.
    """
    try:
        parsed_url = urlparse(file_url)
        path_parts = parsed_url.path.split("/")

        if len(path_parts) < 3:
            raise ValueError(f"Invalid MinIO URL format: {file_url}")

        bucket_name = path_parts[1]
        object_name = "/".join(path_parts[2:])

        return bucket_name, object_name

    except Exception as e:
        raise ValueError(f"Failed to parse MinIO URL: {file_url} - {e}")
