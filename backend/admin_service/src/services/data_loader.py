import asyncio
from pathlib import Path

import aiofiles
from fastapi.concurrency import run_in_threadpool
from pymongo.errors import OperationFailure

from services.logger import get_logger
from services.minio_management import MinioCRUD
from services.mongo_db_management import MongoDatabaseManager
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
        if not self.required_files:
            raise DataLoaderError("Required files set is empty")
        try:
            if not await self._path_exists(self.content_admin_path):
                logger.error(f"Directory {self.content_admin_path} does not exist")
                raise FileNotFoundError(
                    f"Directory {self.content_admin_path} does not exist"
                )

            if not await self._is_directory(self.content_admin_path):
                logger.error(f"{self.content_admin_path} is not a directory")
                raise NotADirectoryError(
                    f"{self.content_admin_path} is not a directory"
                )

            existing_files = await self._get_existing_files()

            missing_files = self.required_files - existing_files

            if missing_files:
                logger.warning(f"Missing files: {', '.join(sorted(missing_files))}")
                return False

            logger.info("All required files are present")
            return True
        except Exception as e:
            logger.error(f"Error checking files: {e}")
            return False

    async def upload_images_to_minio(
        self, minio_crud: MinioCRUD, bucket_name: str
    ) -> dict:
        try:
            upload_results = {}
            existing_files = await self._get_existing_files()
            tasks = []
            for filename in existing_files:
                if Path(filename).suffix.lower() in settings.ALLOWED_IMAGE_EXTENSIONS:
                    tasks.append(
                        self._upload_single_file(minio_crud, bucket_name, filename)
                    )
            results = await asyncio.gather(*tasks, return_exceptions=True)

            image_files = [
                f
                for f in existing_files
                if Path(f).suffix.lower() in settings.ALLOWED_IMAGE_EXTENSIONS
            ]
            for filename, result in zip(image_files, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to upload {filename}: {result}")
                    raise DataLoaderError(f"Failed to upload {filename}: {result}")
                else:
                    upload_results[filename] = result
                    logger.info(f"Successfully uploaded {filename} to MinIO")

            return upload_results

        except Exception as e:
            logger.error(f"Error during MinIO upload process: {e}")
            raise DataLoaderError(f"MinIO upload failed: {e}")

    async def check_minio_files_existence(
        self, minio_crud: MinioCRUD, bucket_name: str
    ) -> bool:
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
                f"Found {len(image_files)} image files in MinIO bucket '{bucket_name}'"
            )
            return len(image_files) > 1

        except Exception as e:
            logger.error(f"Error checking MinIO files: {e}")
            return False

    async def save_content_to_mongodb(
        self,
        db_manager: MongoDatabaseManager,
        collection_name: str,
        minio_urls_mapping: dict,
        content_data: list,
    ) -> int:
        try:
            # Transform data: replace filenames with MinIO URLs
            transformed_data = []
            for item in content_data:
                # Create a copy to avoid modifying original data
                transformed_item = item.copy()

                # Replace local filename with MinIO URL if exists
                original_filename = transformed_item.get("image_url")
                if original_filename and original_filename in minio_urls_mapping:
                    transformed_item["image_url"] = minio_urls_mapping[
                        original_filename
                    ]
                    logger.debug(f"Replaced {original_filename} with MinIO URL")
                else:
                    logger.warning(f"No MinIO URL found for {original_filename}")

                transformed_data.append(transformed_item)

            db = db_manager.db
            collection = db[collection_name]

            result = await collection.insert_many(transformed_data)
            inserted_count = len(result.inserted_ids)

            logger.info(
                f"Successfully inserted {inserted_count} documents into '{collection_name}' collection"
            )
            return inserted_count

        except OperationFailure as e:
            logger.error(
                f"MongoDB operation failed for collection '{collection_name}': {e}"
            )
            raise DataLoaderError(f"Database operation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving to MongoDB: {e}")
            raise DataLoaderError(f"Failed to save content: {e}")

    async def _upload_single_file(
        self, minio_crud: MinioCRUD, bucket_name: str, filename: str
    ) -> str:
        """Helper method to upload a single file to MinIO"""
        file_path = self.content_admin_path / filename

        # Read file content asynchronously
        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()

        # Upload to MinIO using the existing MinioCRUD class
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
