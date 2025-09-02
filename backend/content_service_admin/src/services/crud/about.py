from typing import Any, Optional
from base import BaseCRUD


class AboutCRUD(BaseCRUD):
    """CRUD operations for about collection."""

    async def get_about_content(
        self, lang: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get about content, optionally filtered by language."""
        if not lang:
            return await self.get_all()

        # Агрегация для фильтрации на уровне MongoDB
        pipeline = [
            {
                "$project": {
                    "image": 1,
                    "title": {
                        "$cond": [
                            {"$ifNull": [f"$translations.{lang}.title", False]},
                            f"$translations.{lang}.title",
                            {
                                "$cond": [
                                    {"$ifNull": ["$translations.en.title", False]},
                                    "$translations.en.title",
                                    {
                                        "$arrayElemAt": [
                                            {"$objectToArray": "$translations.title"},
                                            1,
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    "description": {
                        "$cond": [
                            {"$ifNull": [f"$translations.{lang}.description", False]},
                            f"$translations.{lang}.description",
                            {
                                "$cond": [
                                    {
                                        "$ifNull": [
                                            "$translations.en.description",
                                            False,
                                        ]
                                    },
                                    "$translations.en.description",
                                    {
                                        "$arrayElemAt": [
                                            {
                                                "$objectToArray": "$translations.description"
                                            },
                                            1,
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                }
            }
        ]

        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def get_about_content_simple(
        self, lang: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Simple version - get all data and filter in Python."""
        all_data = await self.get_all()

        if not lang:
            return all_data

        filtered_data = []
        for item in all_data:
            if "translations" in item and lang in item["translations"]:
                filtered_item = {
                    "image": item.get("image", ""),
                    "title": item["translations"][lang].get("title", ""),
                    "description": item["translations"][lang].get("description", ""),
                }
                filtered_data.append(filtered_item)

        return filtered_data

    async def get_all_languages(self) -> list[str]:
        """Get list of all available languages in the about content."""
        pipeline = [
            {"$project": {"languages": {"$objectToArray": "$translations"}}},
            {"$unwind": "$languages"},
            {"$group": {"_id": "$languages.k"}},
            {"$sort": {"_id": 1}},
        ]

        cursor = self.collection.aggregate(pipeline)
        languages = await cursor.to_list(length=None)
        return [lang["_id"] for lang in languages]
