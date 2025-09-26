from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from content_admin.models.about import (
    AboutFullResponse,
    AboutTranslatedResponse,
)
from services.logger import get_logger
from settings import settings

logger = get_logger(settings.CONTENT_ADMIN_ABOUT_NAME)


class AboutCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.about

    # CREATE
    async def create(self, data: dict[str, Any]) -> str:
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    # READ
    async def read_all(self, lang: str | None = None) -> list[dict[str, Any]]:
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
                AboutTranslatedResponse(**item).model_dump()
                for item in results
            ]

    async def read_one(
        self, document_id: str, lang: str | None = None
    ) -> dict[str, Any] | None:
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
            if not lang:
                result = await self.collection.find_one(
                    {"_id": ObjectId(document_id)}
                )
                return (
                    AboutFullResponse(**result).model_dump()
                    if result
                    else None
                )
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
                    AboutTranslatedResponse(**result).model_dump()
                    if result
                    else None
                )
        except InvalidId:
            return None

    # UPDATE
    async def update(
        self, document_id: str, update_data: dict[str, Any]
    ) -> bool:
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
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)}, {"$set": update_data}
        )

        if result.modified_count == 0:
            logger.debug(
                f"Document with id {document_id} not found for update"
            )
            return False

        logger.info(f"Successfully updated document with id {document_id}")
        return True

    # DELETE
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
        result = await self.collection.delete_one(
            {"_id": ObjectId(document_id)}
        )

        if result.deleted_count == 0:
            logger.warning(
                f"Document with id {document_id} not found for deletion"
            )
            return False

        logger.info(f"Successfully deleted document with id {document_id}")
        return True
