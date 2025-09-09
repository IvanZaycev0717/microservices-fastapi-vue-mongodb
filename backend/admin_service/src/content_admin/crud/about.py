from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from content_admin.models.about import (AboutFullResponse,
                                        AboutTranslatedResponse)
from services.logger import get_logger

logger = get_logger("about-crud")


class AboutCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.about

    async def read_all(self, lang: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            if not lang or (lang not in ("en", "ru")):
                cursor = self.collection.find()
                results = await cursor.to_list(length=None)
                return [AboutFullResponse(**item).model_dump() for item in results]
            else:
                pipeline = [
                    {
                        "$project": {
                            "image_url": 1,
                            "title": f"$translations.{lang}.title",
                            "description": f"$translations.{lang}.description",
                            "_id": 1,
                        }
                    }
                ]
                cursor = await self.collection.aggregate(pipeline)
                results = await cursor.to_list(length=None)
                return [
                    AboutTranslatedResponse(**item).model_dump() for item in results
                ]

        except Exception as e:
            logger.error(f"Database error in fetch: {e}")
            raise

    async def read_one(
        self, document_id: str, lang: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a single document by ID with optional language filtering.

        Args:
            document_id: String representation of the document's ObjectId.
            lang: Optional language code ('en' or 'ru') for translated response.

        Returns:
            Dict representation of AboutFullResponse or AboutTranslatedResponse if found,
            None otherwise.

        Raises:
            ValueError: If the provided document_id is not a valid ObjectId.
            Exception: For any other database errors during fetch operation.
        """
        try:
            if not ObjectId.is_valid(document_id):
                raise ValueError(f"Invalid ObjectId format: {document_id}")

            if not lang:
                result = await self.collection.find_one({"_id": ObjectId(document_id)})
                return AboutFullResponse(**result).model_dump() if result else None
            else:
                pipeline = [
                    {"$match": {"_id": ObjectId(document_id)}},
                    {
                        "$project": {
                            "image_url": 1,
                            "title": f"$translations.{lang}.title",
                            "description": f"$translations.{lang}.description",
                            "_id": 1,
                        }
                    },
                ]
                cursor = self.collection.aggregate(pipeline)
                results = await cursor.to_list(length=1)
                result = results[0] if results else None
                return (
                    AboutTranslatedResponse(**result).model_dump() if result else None
                )

        except Exception as e:
            logger.error(f"Database error in read_one: {e}")
            raise

    async def create(self, data: dict[str, Any]) -> str:
        try:
            result = await self.collection.insert_one(data)
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Database error in create: {e}")
            raise

    async def update(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a document by its ID with provided data.

        Args:
            document_id: The string representation of the document's ObjectId.
            update_data: Dictionary with fields to update.

        Returns:
            bool: True if document was successfully updated, False if document not found.

        Raises:
            ValueError: If the provided document_id is not a valid ObjectId.
            Exception: For any other database errors during update.
        """
        try:
            if not ObjectId.is_valid(document_id):
                raise ValueError(f"Invalid ObjectId format: {document_id}")

            result = await self.collection.update_one(
                {"_id": ObjectId(document_id)}, {"$set": update_data}
            )

            if result.modified_count == 0:
                logger.warning(f"Document with id {document_id} not found for update")
                return False

            logger.info(f"Successfully updated document with id {document_id}")
            return True

        except ValueError as e:
            logger.error(f"Validation error in update: {e}")
            raise
        except Exception as e:
            logger.error(f"Database error in update: {e}")
            raise

    async def delete(self, document_id: str) -> bool:
        """Delete a document by its ID from the collection.

        Args:
            document_id: The string representation of the document's ObjectId.

        Returns:
            bool: True if document was successfully deleted, False if document not found.

        Raises:
            ValueError: If the provided document_id is not a valid ObjectId.
            Exception: For any other database errors during deletion.
        """
        try:
            if not ObjectId.is_valid(document_id):
                raise ValueError(f"Invalid ObjectId format: {document_id}")

            result = await self.collection.delete_one({"_id": ObjectId(document_id)})

            if result.deleted_count == 0:
                logger.warning(f"Document with id {document_id} not found for deletion")
                return False

            logger.info(f"Successfully deleted document with id {document_id}")
            return True

        except ValueError as e:
            logger.error(f"Validation error in delete: {e}")
            raise
        except Exception as e:
            logger.error(f"Database error in delete: {e}")
            raise
