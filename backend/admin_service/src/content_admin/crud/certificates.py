from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from services.logger import get_logger
from settings import settings

logger = get_logger(settings.CONTENT_SERVICE_CERTIFICATES_NAME)


class CertificatesCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.certificates

    async def read_all(self, sort: str = "date_desc") -> List[Dict[str, Any]]:
        try:
            if sort.startswith("date"):
                sort_field = "date"
                sort_direction = -1 if sort.endswith("desc") else 1
            else:
                sort_field = "popularity"
                sort_direction = 1 if sort.endswith("desc") else -1

            cursor = self.collection.find({}).sort(sort_field, sort_direction)
            results = await cursor.to_list(length=None)

            transformed_results = []
            for item in results:
                transformed_results.append(
                    {
                        "id": str(item["_id"]),
                        "thumb": item["thumb"],
                        "src": item["src"],
                        "date": item["date"].isoformat()
                        if hasattr(item["date"], "isoformat")
                        else item["date"],
                        "popularity": item["popularity"],
                        "alt": item["alt"],
                    }
                )
            return transformed_results
        except Exception as e:
            logger.exception(f"Database error in read_all: {e}")
            raise

    async def create(self, certificate_data: dict[str, Any]) -> str:
        """Create new certificate document in MongoDB collection.

        Args:
            certificate_data: Dictionary with certificate data.

        Returns:
            str: String representation of inserted document's ObjectId.

        Raises:
            Exception: If database operation fails.
        """
        try:
            result = await self.collection.insert_one(certificate_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.exception(f"Database error in create: {e}")
            raise

    async def read_one_by_id(
        self, certificate_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get single certificate by ID.

        Args:
            certificate_id: MongoDB document ID as string.

        Returns:
            Optional[Dict]: Certificate data if found, None otherwise.

        Raises:
            InvalidId: If certificate_id is not a valid ObjectId.
        """
        try:
            object_id = ObjectId(certificate_id)
            item = await self.collection.find_one({"_id": object_id})

            if not item:
                return None

            return {
                "id": str(item["_id"]),
                "src": item["src"],
                "thumb": item["thumb"],
                "date": item["date"].isoformat()
                if hasattr(item["date"], "isoformat")
                else item["date"],
                "popularity": item["popularity"],
                "alt": item["alt"],
            }

        except Exception as e:
            logger.exception(f"Database error in read_one_by_id: {e}")
            raise

    async def update(
        self, certificate_id: str, update_data: Dict[str, Any]
    ) -> bool:
        """Update certificate document by ID.

        Args:
            certificate_id: MongoDB document ID as string.
            update_data: Dictionary with fields to update.

        Returns:
            bool: True if document was updated, False if not found.

        Raises:
            InvalidId: If certificate_id is not a valid ObjectId.
        """
        try:
            object_id = ObjectId(certificate_id)
            result = await self.collection.update_one(
                {"_id": object_id}, {"$set": update_data}
            )
            return result.modified_count > 0

        except InvalidId:
            logger.warning(f"Invalid certificate ID format: {certificate_id}")
            return False
        except Exception as e:
            logger.exception(f"Database error in update: {e}")
            raise

    async def delete(self, certificate_id: str) -> bool:
        """Delete certificate document by ID.

        Args:
            certificate_id: MongoDB document ID as string.

        Returns:
            bool: True if document was deleted, False if not found.

        Raises:
            InvalidId: If certificate_id is not a valid ObjectId.
        """
        try:
            object_id = ObjectId(certificate_id)
            result = await self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0

        except InvalidId:
            logger.warning(f"Invalid certificate ID format: {certificate_id}")
            return False
        except Exception as e:
            logger.exception(f"Database error in delete: {e}")
            raise
