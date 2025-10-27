import asyncio
from datetime import datetime
from pathlib import Path

import aiofiles
from bson import ObjectId
from fastapi.concurrency import run_in_threadpool
from pymongo.errors import DuplicateKeyError, OperationFailure

from services.logger import get_logger
from services.minio_management import MinioCRUD
from services.mongo_db_management import MongoDatabaseManager
from services.password_processor import get_password_hash
from settings import settings

logger = get_logger("data_loader")


class DataLoaderError(Exception):
    """Base exception for DataLoader"""

    pass


class DataLoader:
    def __init__(self, content_admin_path: Path, required_files: set[str]):
        self.content_admin_path = content_admin_path
        self.required_files = required_files

    async def check_loading_files(self) -> bool:
        """Check if all required files are present in the content admin directory.

        Returns:
            bool: True if all required files exist, False otherwise.

        Raises:
            DataLoaderError: If required files set is empty.
            FileNotFoundError: If content admin directory does not exist.
            NotADirectoryError: If content admin path is not a directory.
        """
        if not self.required_files:
            raise DataLoaderError("Required files set is empty")
        try:
            if not await self._path_exists(self.content_admin_path):
                logger.exception(
                    f"Directory {self.content_admin_path} does not exist"
                )
                raise FileNotFoundError(
                    f"Directory {self.content_admin_path} does not exist"
                )

            if not await self._is_directory(self.content_admin_path):
                logger.exception(
                    f"{self.content_admin_path} is not a directory"
                )
                raise NotADirectoryError(
                    f"{self.content_admin_path} is not a directory"
                )

            existing_files = await self._get_existing_files()

            missing_files = self.required_files - existing_files

            if missing_files:
                logger.warning(
                    f"Missing files: {', '.join(sorted(missing_files))}"
                )
                return False

            logger.info("All required files are present")
            return True
        except Exception as e:
            logger.exception(f"Error checking files: {e}")
            return False

    async def upload_images_to_minio(
        self, minio_crud: MinioCRUD, bucket_name: str
    ) -> dict:
        """Upload all image files to MinIO storage.

        Args:
            minio_crud (MinioCRUD): MinIO CRUD operations instance.
            bucket_name (str): Name of the MinIO bucket.

        Returns:
            dict: Dictionary mapping filenames to their upload URLs.

        Raises:
            DataLoaderError: If upload process fails for any file.
        """
        try:
            upload_results = {}
            existing_files = await self._get_existing_files()
            tasks = []
            for filename in existing_files:
                if (
                    Path(filename).suffix.lower()
                    in settings.ALLOWED_IMAGE_EXTENSIONS
                ):
                    tasks.append(
                        self._upload_single_file(
                            minio_crud, bucket_name, filename
                        )
                    )
            results = await asyncio.gather(*tasks, return_exceptions=True)

            image_files = [
                f
                for f in existing_files
                if Path(f).suffix.lower() in settings.ALLOWED_IMAGE_EXTENSIONS
            ]
            for filename, result in zip(image_files, results):
                if isinstance(result, Exception):
                    logger.exception(f"Failed to upload {filename}: {result}")
                    if "BucketAlreadyOwnedByYou" in str(result):
                        logger.info(f"Bucket already exists for {filename}, skipping")
                        continue
                    raise DataLoaderError(
                        f"Failed to upload {filename}: {result}"
                    )
                else:
                    upload_results[filename] = result
                    logger.info(f"Successfully uploaded {filename} to MinIO")

            return upload_results

        except Exception as e:
            logger.exception(f"Error during MinIO upload process: {e}")
            raise DataLoaderError(f"MinIO upload failed: {e}")

    async def check_minio_files_existence(
        self, minio_crud: MinioCRUD, bucket_name: str
    ) -> bool:
        """Check if image files exist in MinIO bucket.

        Args:
            minio_crud (MinioCRUD): MinIO CRUD operations instance.
            bucket_name (str): Name of the MinIO bucket.

        Returns:
            bool: True if at least one image file exists in the bucket, False otherwise.
        """
        try:
            objects = await run_in_threadpool(
                lambda: list(minio_crud.client.list_objects(bucket_name))
            )

            image_files = [
                obj.object_name
                for obj in objects
                if Path(obj.object_name).suffix.lower()
                in settings.ALLOWED_IMAGE_EXTENSIONS
            ]

            logger.info(
                f"Found {len(image_files)} "
                f"image files in MinIO bucket '{bucket_name}'"
            )

            return len(image_files) >= 1

        except Exception as e:
            logger.exception(f"Error checking MinIO files: {e}")
            return False

    async def save_content_to_mongodb(
        self,
        db_manager: MongoDatabaseManager,
        collection_name: str,
        minio_urls_mapping: dict,
        content_data: list,
    ) -> int:
        """Save content data to MongoDB collection with MinIO URL replacements.

        Args:
            db_manager (MongoDatabaseManager): MongoDB manager instance.
            collection_name (str): Name of the target collection.
            minio_urls_mapping (dict): Dictionary mapping filenames to MinIO URLs.
            content_data (list): List of content items to save.

        Returns:
            int: Number of documents successfully inserted.

        Raises:
            DataLoaderError: If database operation fails or unexpected error occurs.
        """
        try:
            # Transform data: replace filenames with MinIO URLs
            transformed_data = []
            for item in content_data:
                # Create a copy to avoid modifying original data
                transformed_item = item.copy()

                # Replace local filename with MinIO URL if exists
                original_filename = transformed_item.get("image_url")
                if (
                    original_filename
                    and original_filename in minio_urls_mapping
                ):
                    transformed_item["image_url"] = minio_urls_mapping[
                        original_filename
                    ]
                    logger.debug(
                        f"Replaced {original_filename} with MinIO URL"
                    )
                else:
                    logger.warning(
                        f"No MinIO URL found for {original_filename}"
                    )

                transformed_data.append(transformed_item)

            db = db_manager.db
            collection = db[collection_name]

            result = await collection.insert_many(transformed_data)
            inserted_count = len(result.inserted_ids)

            logger.info(
                f"Successfully inserted {inserted_count} "
                f"documents into '{collection_name}' collection"
            )
            return inserted_count

        except OperationFailure as e:
            logger.exception(
                f"MongoDB operation failed "
                f"for collection '{collection_name}': {e}"
            )
            raise DataLoaderError(f"Database operation failed: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error saving to MongoDB: {e}")
            raise DataLoaderError(f"Failed to save content: {e}")

    async def load_admin_user_to_auth_db(
        self,
        db_manager: MongoDatabaseManager,
        admin_email: str,
        admin_password: str,
    ) -> bool:
        """
        Load admin user into auth database users collection.

        Args:
            db_manager: MongoDB manager for auth database
            admin_email: Admin email address
            admin_password: Admin plain text password

        Returns:
            bool: True if admin was created or already exists, False on error
        """
        try:
            logger.info("Loading admin user")

            collection = db_manager.client[
                settings.AUTH_ADMIN_MONGO_DATABASE_NAME
            ]["users"]

            existing_admin = await collection.find_one({"email": admin_email})
            if existing_admin:
                logger.info(f"Admin user already exists: {admin_email}")
                return True

            hashed_password = get_password_hash(admin_password)

            admin_user = {
                "_id": ObjectId(),
                "email": admin_email,
                "password_hash": hashed_password,
                "is_banned": False,
                "roles": ["admin", "user"],
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "last_login_at": None,
            }

            result = await collection.insert_one(admin_user)

            if result.inserted_id:
                logger.info(f"Admin user created successfully: {admin_email}")
                return True
            else:
                logger.error(f"Failed to create admin user: {admin_email}")
                return False

        except DuplicateKeyError:
            logger.warning(
                f"Admin user already exists (duplicate key): {admin_email}"
            )
            return True

        except Exception as e:
            logger.exception(f"Error loading admin user {admin_email}: {e}")
            return False

    async def _upload_single_file(
        self, minio_crud: MinioCRUD, bucket_name: str, filename: str
    ) -> str:
        """Upload a single file to MinIO storage.

        Args:
            minio_crud (MinioCRUD): MinIO CRUD operations instance.
            bucket_name (str): Name of the MinIO bucket.
            filename (str): Name of the file to upload.

        Returns:
            str: URL of the uploaded file in MinIO.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        file_path = self.content_admin_path / filename

        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()

        return await minio_crud.upload_file(bucket_name, filename, file_data)

    async def _path_exists(self, path: Path) -> bool:
        """Async check if path exists"""
        return await asyncio.to_thread(path.exists)

    async def _is_directory(self, path: Path) -> bool:
        """Async check if path is directory"""
        return await asyncio.to_thread(path.is_dir)

    async def _get_existing_files(self) -> set[str]:
        """Async get existing files in directory"""

        def sync_get_files():
            return {
                file.name
                for file in self.content_admin_path.iterdir()
                if file.is_file()
            }

        return await asyncio.to_thread(sync_get_files)
