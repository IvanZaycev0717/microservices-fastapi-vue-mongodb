from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from services.logger import get_logger
from settings import settings

logger = get_logger(settings.CONTENT_ADMIN_PROJECTS_NAME)


class PublicationsCRUD:
    """Handles publications database operations.

    Attributes:
        collection: MongoDB collection instance for publications data.
    """

    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.publications

    # CREATE
    async def create(self, publication_data: dict[str, Any]):
        """Create a new publication in the database.

        Args:
            publication_data (dict[str, Any]): Publication data to insert.

        Returns:
            str: String representation of the inserted document's ID.
        """
        result = await self.collection.insert_one(publication_data)
        return str(result.inserted_id)

    # READ
    async def read_all(
        self, lang: str, sort: str = "date_desc"
    ) -> list[dict[str, Any]]:
        """Retrieve all publications with sorting and language options.

        Args:
            lang (str): Language code for translation ('en' or 'ru').
            sort (str): Sorting criteria ('date_desc', 'date_asc', 'rating_desc').

        Returns:
            list[dict[str, Any]]: list of publication data as dictionaries.
        """
        if sort.startswith("date"):
            sort_field = "date"
            sort_direction = DESCENDING if sort.endswith("desc") else ASCENDING
        else:
            sort_field = "rating"
            sort_direction = DESCENDING

        cursor = self.collection.find({}).sort(sort_field, sort_direction)
        results = await cursor.to_list(length=None)

        transformed_results = []
        for item in results:
            if lang not in ("en", "ru"):
                transformed_results.append(
                    {
                        "id": str(item["_id"]),
                        "title": item["title"],
                        "page": item["page"],
                        "site": item["site"],
                        "rating": item["rating"],
                        "date": item["date"].isoformat()
                        if hasattr(item["date"], "isoformat")
                        else item["date"],
                    }
                )
            else:
                transformed_results.append(
                    {
                        "id": str(item["_id"]),
                        "title": item["title"].get(lang, ""),
                        "page": item["page"],
                        "site": item["site"],
                        "rating": item["rating"],
                        "date": item["date"].isoformat()
                        if hasattr(item["date"], "isoformat")
                        else item["date"],
                    }
                )
        return transformed_results

    async def read_by_id(self, publication_id: str):
        """Retrieve a specific publication by ID.

        Args:
            publication_id (str): ID of the publication to retrieve.

        Returns:
            dict: Publication data as dictionary if found, None otherwise.
        """
        try:
            object_id = ObjectId(publication_id)
            item = await self.collection.find_one({"_id": object_id})
            if not item:
                return None
            return {
                "id": str(item["_id"]),
                "title": item["title"],
                "page": item["page"],
                "site": item["site"],
                "rating": item["rating"],
                "date": item["date"].isoformat()
                if hasattr(item["date"], "isoformat")
                else item["date"],
            }
        except InvalidId:
            logger.exception("Invalid document Id")
            return None

    # UPDATE
    async def update(
        self, publication_id: str, update_data: dict[str, Any]
    ) -> None:
        """Update publication document by ID.

        Args:
            publication_id (str): ID of the publication to update.
            update_data (dict[str, Any]): dictionary containing fields to update.
        """
        await self.collection.update_one(
            {"_id": ObjectId(publication_id)}, {"$set": update_data}
        )

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
