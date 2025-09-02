from typing import Any, Dict, List, Optional

from base import BaseCRUD
from pymongo.asynchronous.collection import AsyncCollection


class PublicationsCRUD(BaseCRUD):
    """CRUD operations for publications collection with language support."""

    def __init__(self, collection: AsyncCollection):
        super().__init__(collection)

    async def get_all_publications(self, lang: str = "en") -> List[Dict[str, Any]]:
        """Get all publications with language-specific titles.

        Args:
            lang (str): Language code ('en' or 'ru'). Defaults to 'en'.

        Returns:
            List[Dict]: Publications with language-specific titles.
        """
        # Projection для выбора только нужных полей с языком
        projection = {
            "_id": 0,  # Исключаем _id
            "id": 1,
            "title": f"$title.{lang}",  # Динамически выбираем язык
            "page": 1,
            "site": 1,
            "rating": 1,
            "date": 1,
        }

        cursor = self.collection.find({}, projection)
        publications = await cursor.to_list(length=None)

        # Преобразуем структуру, если нужно
        for pub in publications:
            if "title" in pub and isinstance(pub["title"], dict):
                pub["title"] = pub["title"].get(lang, "")

        return publications

    async def get_publication_by_id(
        self, publication_id: int, lang: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """Get specific publication by ID with language support.

        Args:
            publication_id (int): ID of the publication.
            lang (str): Language code ('en' or 'ru'). Defaults to 'en'.

        Returns:
            Optional[Dict]: Publication data or None if not found.
        """
        projection = {
            "_id": 0,
            "id": 1,
            "title": f"$title.{lang}",
            "page": 1,
            "site": 1,
            "rating": 1,
            "date": 1,
        }

        publication = await self.collection.find_one({"id": publication_id}, projection)

        if (
            publication
            and "title" in publication
            and isinstance(publication["title"], dict)
        ):
            publication["title"] = publication["title"].get(lang, "")

        return publication

    async def get_publications_by_rating(
        self, min_rating: int, lang: str = "en"
    ) -> List[Dict[str, Any]]:
        """Get publications with rating greater than or equal to min_rating.

        Args:
            min_rating (int): Minimum rating value.
            lang (str): Language code. Defaults to 'en'.

        Returns:
            List[Dict]: Filtered publications.
        """
        projection = {
            "_id": 0,
            "id": 1,
            "title": f"$title.{lang}",
            "page": 1,
            "site": 1,
            "rating": 1,
            "date": 1,
        }

        cursor = self.collection.find({"rating": {"$gte": min_rating}}, projection)
        return await cursor.to_list(length=None)

    async def create_publication(
        self, publication_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new publication.

        Args:
            publication_data (Dict): Publication data including multilingual title.

        Returns:
            Dict: Created publication.

        Example:
            publication_data = {
                "id": 2,
                "title": {
                    "en": "English title",
                    "ru": "Русское название"
                },
                "page": "https://example.com",
                "site": "https://example.org",
                "rating": 20,
                "date": "09.09.2025"
            }
        """
        # Проверяем обязательные поля
        required_fields = ["id", "title", "page", "site", "rating", "date"]
        for field in required_fields:
            if field not in publication_data:
                raise ValueError(f"Missing required field: {field}")

        result = await self.collection.insert_one(publication_data)
        return await self.get_publication_by_id(publication_data["id"])

    async def update_publication_title(
        self, publication_id: int, lang: str, new_title: str
    ) -> Optional[Dict[str, Any]]:
        """Update title for specific language.

        Args:
            publication_id (int): ID of the publication.
            lang (str): Language code ('en' or 'ru').
            new_title (str): New title text.

        Returns:
            Optional[Dict]: Updated publication or None if not found.
        """
        result = await self.collection.update_one(
            {"id": publication_id}, {"$set": {f"title.{lang}": new_title}}
        )

        if result.modified_count:
            return await self.get_publication_by_id(publication_id, lang)
        return None

    async def get_publications_sorted_by_date(
        self, lang: str = "en", descending: bool = True
    ) -> List[Dict[str, Any]]:
        """Get publications sorted by date.

        Args:
            lang (str): Language code. Defaults to 'en'.
            descending (bool): Sort order. True for newest first.

        Returns:
            List[Dict]: Sorted publications.
        """
        projection = {
            "_id": 0,
            "id": 1,
            "title": f"$title.{lang}",
            "page": 1,
            "site": 1,
            "rating": 1,
            "date": 1,
        }

        sort_order = -1 if descending else 1

        cursor = self.collection.find({}, projection).sort("date", sort_order)
        return await cursor.to_list(length=None)
