import io
import json
from urllib.parse import urlparse

from minio import Minio
from starlette.concurrency import run_in_threadpool

from services.logger import get_logger
from settings import settings

logger = get_logger("minio")


class MinioManager:
    """Manager for MinIO client connection and bucket operations.

    Attributes:
        client (Minio): Initialized MinIO client instance.
    """

    def __init__(self) -> None:
        """Initializes MinIO client with configuration from settings."""
        self.client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_API_PORT}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )

    async def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        """Creates bucket with public policy if it doesn't exist.

        Args:
            bucket_name: Name of the bucket to create.

        Returns:
            bool: True if bucket exists or was created successfully.
        """
        try:
            found = await run_in_threadpool(
                self.client.bucket_exists, bucket_name
            )
            if not found:
                await run_in_threadpool(self.client.make_bucket, bucket_name)
                await self.set_public_policy(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating bucket {bucket_name}: {e}")
            return False

    async def set_public_policy(self, bucket_name: str) -> None:
        """Sets public read-only policy for the specified bucket.

        Args:
            bucket_name: Name of the bucket to apply public policy to.
        """
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                },
                {
                    "Effect": "Deny",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:DeleteBucket", "s3:DeleteObject"],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*",
                    ],
                },
            ],
        }
        await run_in_threadpool(
            self.client.set_bucket_policy, bucket_name, json.dumps(policy)
        )


class MinioCRUD(MinioManager):
    """CRUD operations manager for MinIO object storage.

    Attributes:
        minio_host (str): MinIO server host address.
        minio_port (str): MinIO server port number.
    """

    def __init__(self) -> None:
        """Initializes MinIO CRUD manager with connection settings."""
        super().__init__()
        self.minio_host = settings.MINIO_PUBLIC_URL
        self.minio_port = settings.MINIO_API_PORT

    async def upload_file(
        self, bucket_name: str, object_name: str, file_data: bytes
    ) -> str:
        """Uploads file data to existing MinIO bucket.

        Args:
            bucket_name: Name of the bucket to upload to.
            object_name: Name of the object to create.
            file_data: Binary data of the file to upload.

        Returns:
            str: Public URL to access the uploaded file.
        """
        await run_in_threadpool(
            self.client.put_object,
            bucket_name,
            object_name,
            io.BytesIO(file_data),
            len(file_data),
        )
        return f"{settings.MINIO_PUBLIC_URL}/{bucket_name}/{object_name}"

    async def upload_file(
        self, bucket_name: str, object_name: str, file_data: bytes
    ) -> str:
        try:
            await run_in_threadpool(
                self.client.put_object,
                bucket_name,
                object_name,
                io.BytesIO(file_data),
                len(file_data),
            )
            return f"{settings.MINIO_PUBLIC_URL}/{bucket_name}/{object_name}"
        except Exception as e:
            logger.error(f"MinIO upload failed: {e}")
            raise

    async def delete_file(self, bucket_name: str, object_name: str) -> None:
        """Deletes specified object from MinIO storage.

        Args:
            bucket_name: Name of the bucket containing the object.
            object_name: Name of the object to delete.
        """
        await run_in_threadpool(
            self.client.remove_object, bucket_name, object_name
        )
