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
    """Handles about section database operations.

    Attributes:
        collection: MongoDB collection instance for about data.
    """

    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.about

    # CREATE
    async def create(self, data: dict[str, Any]) -> str:
        """Create a new document in the collection.

        Args:
            data (dict[str, Any]): Document data to insert.

        Returns:
            str: String representation of the inserted document's ID.
        """
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    # READ
    async def read_all(self, lang: str | None = None) -> list[dict[str, Any]]:
        """Retrieve all documents from the collection.

        Args:
            lang (str | None): Language code for translation ('en' or 'ru').
                              If None or invalid, returns full response.

        Returns:
            list[dict[str, Any]]: List of documents as dictionaries.
        """
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
        """Retrieve a specific document by ID.

        Args:
            document_id (str): ID of the document to retrieve.
            lang (str | None): Language code for translation ('en' or 'ru').
                              If None, returns full response.

        Returns:
            dict[str, Any] | None: Document data as dictionary if found, None otherwise.
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
        """Update a specific document by ID.

        Args:
            document_id (str): ID of the document to update.
            update_data (dict[str, Any]): Dictionary containing fields to update.

        Returns:
            bool: True if document was successfully updated, False otherwise.
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)}, {"$set": update_data}
        )

        if result.modified_count == 0:
            logger.info(
                f"Document with id {document_id} not found for update"
            )
            return False

        logger.info(f"Successfully updated document with id {document_id}")
        return True

    # DELETE
    async def delete(self, document_id: str) -> bool:
        """Delete a specific document by ID.

        Args:
            document_id (str): ID of the document to delete.

        Returns:
            bool: True if document was successfully deleted, False otherwise.
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
