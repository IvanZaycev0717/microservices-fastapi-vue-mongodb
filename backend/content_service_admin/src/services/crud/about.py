from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from services.logger import get_logger

logger = get_logger('about-crud')


class AboutCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.about

    async def fetch(self, lang: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            if not lang or (lang not in ("en", "ru")):
                cursor = self.collection.find()
                results = await cursor.to_list(length=None)
            else:
                pipeline = [
                    {
                        "$project": {
                            "image": 1,
                            "title": f"$translations.{lang}.title",
                            "description": f"$translations.{lang}.description",
                            "_id": 1,
                        }
                    }
                ]
                cursor = await self.collection.aggregate(pipeline)
                results = await cursor.to_list(length=None)

            return self._convert_objectid_to_str(results)

        except Exception as e:
            logger.error(f"Database error in fetch: {e}")
            raise

    async def fetch_one(
        self, document_id: str, lang: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Получить один документ по ID"""
        try:
            if not lang:
                result = await self.collection.find_one({"_id": ObjectId(document_id)})
            else:
                pipeline = [
                    {"$match": {"_id": ObjectId(document_id)}},
                    {
                        "$project": {
                            "image": 1,
                            "title": f"$translations.{lang}.title",
                            "description": f"$translations.{lang}.description",
                            "_id": 1,
                        }
                    },
                ]
                cursor = self.collection.aggregate(pipeline)
                results = await cursor.to_list(length=1)
                result = results[0] if results else None

            return self._convert_objectid_to_str([result])[0] if result else None

        except Exception as e:
            logger.error(f"Database error in fetch_one: {e}")
            raise

    def _convert_objectid_to_str(
        self, data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Преобразует ObjectId в строки"""
        if not data:
            return []

        converted_data = []
        for item in data:
            if item is None:
                continue

            converted_item = {}
            for key, value in item.items():
                if isinstance(value, ObjectId):
                    converted_item[key] = str(value)
                else:
                    converted_item[key] = value
            converted_data.append(converted_item)

        return converted_data
