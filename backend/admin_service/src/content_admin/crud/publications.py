from typing import Any, Dict, List

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from services.logger import get_logger
from settings import settings

logger = get_logger(settings.CONTENT_ADMIN_PROJECTS_NAME)


class PublicationsCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.publications

    # CREATE
    async def create(self, publication_data: dict[str, Any]):
        result = await self.collection.insert_one(publication_data)
        return str(result.inserted_id)

    # READ
    async def read_all(
        self, lang: str, sort: str = "date_desc"
    ) -> List[Dict[str, Any]]:
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
        self, publication_id: str, update_data: Dict[str, Any]
    ) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(publication_id)}, {"$set": update_data}
        )

    # DELETE
    async def delete(self, document_id: str) -> bool:
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
