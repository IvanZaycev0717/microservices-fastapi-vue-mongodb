from typing import Any, Dict, List
from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from services.logger import get_logger
from settings import settings
from bson.errors import InvalidId


logger = get_logger(settings.CONTENT_SERVICE_PROJECTS_NAME)


class PublicationsCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.publications

    async def read_all(
        self, lang: str, sort: str = "date_desc"
    ) -> List[Dict[str, Any]]:
        try:
            if sort.startswith("date"):
                sort_field = "date"
                sort_direction = -1 if sort.endswith("desc") else 1
            else:
                sort_field = "rating"
                sort_direction = -1 if sort.endswith("desc") else 1

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

        except Exception as e:
            logger.exception(f"Database error in read_all: {e}")
            raise

    async def create(self, publication_data: dict[str, Any]):
        try:
            result = await self.collection.insert_one(publication_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.exception(f"Database error in create: {e}")
            raise

    async def read_by_id(self, publication_id: str):
        try:
            object_id = ObjectId(publication_id)
            item = await self.collection.find_one({"_id": object_id})
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
            return None
    
    async def update(self, publication_id: str, update_data: Dict[str, Any]) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(publication_id)}, {"$set": update_data}
        )
