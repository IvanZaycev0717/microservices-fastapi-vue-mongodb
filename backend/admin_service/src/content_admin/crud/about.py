from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from content_admin.models.about import AboutFullResponse, AboutTranslatedResponse
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
        """Получить один документ по ID"""
        try:
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
            logger.error(f"Database error in fetch_one: {e}")
            raise

    async def create(self, data: dict[str, Any]) -> str:
        try:
            result = await self.collection.insert_one(data)
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Database error in create: {e}")
            raise
