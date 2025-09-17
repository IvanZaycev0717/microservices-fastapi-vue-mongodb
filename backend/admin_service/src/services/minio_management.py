import io
import json
from urllib.parse import urlparse

from minio import Minio
from starlette.concurrency import run_in_threadpool

from settings import settings


class MinioManager:
    """Manager for MinIO client connection and bucket configuration.

    Handles the initialization of MinIO client and provides methods
    for bucket management operations such as setting public access policies.

    Attributes:
        client (Minio): Initialized MinIO client instance.
    """

    def __init__(self) -> None:
        """Initialize MinIO client with settings from configuration.

        Creates a MinIO client instance using connection parameters from
        application settings including host, port, and authentication credentials.

        Raises:
            ValueError: If required MinIO configuration settings are missing.
        """
        self.client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )

    async def set_public_policy(self, bucket_name: str) -> None:
        """Set public read-only policy for the specified bucket.

        Configures the bucket policy to allow public read access to all objects
        within the bucket. This enables anyone to download files from the bucket
        without authentication.

        Args:
            bucket_name: Name of the bucket to apply the public policy to.

        Raises:
            S3Error: If MinIO operation fails.
            Exception: For any other unexpected errors during policy setting.
        """
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                }
            ],
        }
        await run_in_threadpool(
            self.client.set_bucket_policy, bucket_name, json.dumps(policy)
        )


class MinioCRUD(MinioManager):
    """CRUD operations manager for MinIO object storage.

    Extends MinioManager to provide file operations including upload,
    update, and delete functionality. Handles URL generation for
    stored objects.

    Attributes:
        minio_host (str): MinIO server host address from settings.
        minio_port (str): MinIO server port number from settings.
    """

    def __init__(self) -> None:
        """Initialize MinIO CRUD manager with connection settings.

        Inherits client initialization from MinioManager and stores
        additional host/port information for URL generation.
        """
        super().__init__()
        self.minio_host = settings.MINIO_HOST
        self.minio_port = settings.MINIO_PORT

    async def upload_file(
        self, bucket_name: str, object_name: str, file_data: bytes
    ) -> str:
        """Upload file data to MinIO storage and return public URL.

        Checks if bucket exists, creates it with public policy if not,
        then uploads the file data. Returns publicly accessible URL.

        Args:
            bucket_name: Name of the bucket to upload to.
            object_name: Name of the object (file) to create.
            file_data: Binary data of the file to upload.

        Returns:
            str: Public URL to access the uploaded file.

        Raises:
            S3Error: If MinIO operation fails (bucket creation, upload).
            Exception: For any other unexpected errors during upload.
        """
        bucket_exists = await run_in_threadpool(
            self.client.bucket_exists, bucket_name
        )

        if not bucket_exists:
            await run_in_threadpool(self.client.make_bucket, bucket_name)
            await self.set_public_policy(bucket_name)

        await run_in_threadpool(
            self.client.put_object,
            bucket_name,
            object_name,
            io.BytesIO(file_data),
            len(file_data),
        )

        return f"http://{self.minio_host}:{self.minio_port}/{bucket_name}/{object_name}"

    async def update_file(self, file_url: str, new_file_data: bytes) -> str:
        """Update existing file in MinIO storage with new data.

        Parses the file URL to extract bucket and object names, then
        uploads new data to the same location, effectively replacing
        the existing file.

        Args:
            file_url: URL of the existing file to update.
            new_file_data: New binary data to replace existing file.

        Returns:
            str: Original file URL (location remains unchanged).

        Raises:
            ValueError: If URL parsing fails or invalid URL format.
            S3Error: If MinIO upload operation fails.
        """
        parsed_url = urlparse(file_url)
        bucket_name = parsed_url.path.split("/")[1]
        object_name = "/".join(parsed_url.path.split("/")[2:])

        await self.upload_file(bucket_name, object_name, new_file_data)
        return file_url

    async def delete_file(self, bucket_name: str, object_name: str) -> None:
        """Delete specified object from MinIO storage.

        Permanently removes the object from the specified bucket.
        This operation cannot be undone.

        Args:
            bucket_name: Name of the bucket containing the object.
            object_name: Name of the object (file) to delete.

        Raises:
            S3Error: If MinIO delete operation fails or object not found.
            Exception: For any other unexpected errors during deletion.
        """
        await run_in_threadpool(
            self.client.remove_object, bucket_name, object_name
        )
