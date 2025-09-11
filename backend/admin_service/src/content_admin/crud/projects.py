from typing import Any, Dict, List

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from services.logger import get_logger

logger = get_logger("projects-crud")


class ProjectsCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.projects

    async def read_all(
        self, lang: str = "en", sort: str = "date_desc"
    ) -> List[Dict[str, Any]]:
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
                    "id": item["_id"],
                    "title": item["title"].get(
                        lang, item["title"].get("en", "")
                    ),
                    "thumbnail": item["thumbnail"],
                    "image": item["image"],
                    "description": item["description"].get(
                        lang, item["description"].get("en", "")
                    ),
                    "link": item["link"],
                    "date": item["date"].isoformat()
                    if hasattr(item["date"], "isoformat")
                    else item["date"],
                    "popularity": item["popularity"],
                }
            )
        return transformed_results

    async def create(self, project_data: dict[str, Any]) -> str:
        """Create new project document in MongoDB collection.

        Args:
            project_data: Dictionary with project data including multilingual fields.

        Returns:
            str: String representation of inserted document's ObjectId.

        Raises:
            Exception: If database operation fails.
        """
        try:
            
            result = await self.collection.insert_one(project_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Database error in create: {e}")
            raise
