from typing import Any, Dict, List

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from services.logger import get_logger
from settings import settings

logger = get_logger(settings.CONTENT_ADMIN_PROJECTS_NAME)


class ProjectsCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.projects

    # CREATE
    async def create(self, project_data: dict[str, Any]) -> str:
        """Create new project document in MongoDB collection.

        Args:
            project_data: Dictionary with project data including multilingual fields.

        Returns:
            str: String representation of inserted document's ObjectId.

        Raises:
            Exception: If database operation fails.
        """
        result = await self.collection.insert_one(project_data)
        return str(result.inserted_id)

    # READ
    async def read_all(
        self, lang: str, sort: str = "date_desc"
    ) -> List[Dict[str, Any]]:
        if sort.startswith("date"):
            sort_field = "date"
            sort_direction = DESCENDING if sort.endswith("desc") else ASCENDING
        else:
            sort_field = "popularity"
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
                        "thumbnail": item["thumbnail"],
                        "image": item["image"],
                        "description": item["description"],
                        "link": item["link"],
                        "date": item["date"].isoformat()
                        if hasattr(item["date"], "isoformat")
                        else item["date"],
                        "popularity": item["popularity"],
                    }
                )
            else:
                transformed_results.append(
                    {
                        "id": str(item["_id"]),
                        "title": item["title"].get(lang, ""),
                        "thumbnail": item["thumbnail"],
                        "image": item["image"],
                        "description": item["description"].get(lang, ""),
                        "link": item["link"],
                        "date": item["date"].isoformat()
                        if hasattr(item["date"], "isoformat")
                        else item["date"],
                        "popularity": item["popularity"],
                    }
                )
        return transformed_results

    async def read_by_id(self, project_id: str, lang: str) -> Dict[str, Any]:
        """Retrieve a project by ID with optional language translation.

        Args:
            project_id (str): ID of the project to retrieve.
            lang (str): Language code for translation ('en' or 'ru').

        Returns:
            Dict[str, Any]: Project data as dictionary if found, None otherwise.
        """
        try:
            object_id = ObjectId(project_id)
            item = await self.collection.find_one({"_id": object_id})
            if not item:
                return None

            if lang not in ("en", "ru"):
                return {
                    "id": str(item["_id"]),
                    "title": item["title"],
                    "thumbnail": item["thumbnail"],
                    "image": item["image"],
                    "description": item["description"],
                    "link": item["link"],
                    "date": item["date"].isoformat()
                    if hasattr(item["date"], "isoformat")
                    else item["date"],
                    "popularity": item["popularity"],
                }
            else:
                return {
                    "id": str(item["_id"]),
                    "title": item["title"].get(lang, ""),
                    "thumbnail": item["thumbnail"],
                    "image": item["image"],
                    "description": item["description"].get(lang, ""),
                    "link": item["link"],
                    "date": item["date"].isoformat()
                    if hasattr(item["date"], "isoformat")
                    else item["date"],
                    "popularity": item["popularity"],
                }
        except InvalidId:
            logger.exception("Invalid document Id")
            return None

    # UPDATE
    async def update(
        self, project_id: str, update_data: Dict[str, Any]
    ) -> None:
        """Update project document by ID.

        Args:
            project_id (str): ID of the project to update.
            update_data (Dict[str, Any]): Dictionary containing fields to update.
        """
        await self.collection.update_one(
            {"_id": ObjectId(project_id)}, {"$set": update_data}
        )

    # DELETE
    async def delete(self, document_id: str) -> bool:
        """Delete project document by ID.

        Args:
            document_id: MongoDB document ID as string.

        Returns:
            bool: True if document was deleted, False if not found.

        Raises:
            InvalidId: If document_id is not a valid ObjectId.
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
