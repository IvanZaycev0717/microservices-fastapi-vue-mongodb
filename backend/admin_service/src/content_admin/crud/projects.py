from typing import Any, Dict, List
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase


class ProjectsCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.projects

    async def read_all(
        self, lang: str = "en", sort: str = "date_desc"
    ) -> List[Dict[str, Any]]:
        sort_field = "date" if sort.startswith("date") else "popularity"
        sort_direction = -1 if sort.endswith("desc") else 1

        cursor = self.collection.find({}).sort(sort_field, sort_direction)
        results = await cursor.to_list(length=None)

        transformed_results = []
        for item in results:
            transformed_results.append(
                {
                    "id": item["id"],
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
