from typing import List, Optional, Dict, Any
from pymongo.asynchronous.collection import AsyncCollection
from base import BaseCRUD


class ProjectsCRUD(BaseCRUD):
    """CRUD operations for projects collection with language support and sorting."""

    def __init__(self, collection: AsyncCollection):
        super().__init__(collection)

    async def get_all_projects(
        self, lang: str = "en", sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all projects with language support and optional sorting.

        Args:
            lang (str): Language code ('en' or 'ru'). Defaults to 'en'.
            sort (Optional[str]): Sorting option.
                Options: 'date_desc', 'date_asc', 'popularity_desc', 'popularity_asc'
                Defaults to None (no sorting).

        Returns:
            List[Dict]: List of projects with language-specific fields.
        """
        # Projection для выбора нужных полей с языком
        projection = {
            "_id": 0,
            "id": 1,
            "title": f"$title.{lang}",
            "thumbnail": 1,
            "image": 1,
            "description": f"$description.{lang}",
            "link": 1,
            "date": 1,
            "popularity": 1,
        }

        sort_mapping = {
            "date_desc": [("date", -1)],
            "date_asc": [("date", 1)],
            "popularity_desc": [("popularity", -1)],
            "popularity_asc": [("popularity", 1)],
            None: None,
        }

        sort_criteria = sort_mapping.get(sort)

        if sort_criteria:
            cursor = self.collection.find({}, projection).sort(sort_criteria)
        else:
            cursor = self.collection.find({}, projection)

        projects = await cursor.to_list(length=None)

        # Обеспечиваем fallback для языков
        for project in projects:
            if isinstance(project.get("title"), dict):
                project["title"] = project["title"].get(lang, "")
            if isinstance(project.get("description"), dict):
                project["description"] = project["description"].get(lang, "")

        return projects

    async def get_project_by_id(
        self, project_id: int, lang: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """Get specific project by ID with language support.

        Args:
            project_id (int): ID of the project.
            lang (str): Language code ('en' or 'ru'). Defaults to 'en'.

        Returns:
            Optional[Dict]: Project data or None if not found.
        """
        projection = {
            "_id": 0,
            "id": 1,
            "title": f"$title.{lang}",
            "thumbnail": 1,
            "image": 1,
            "description": f"$description.{lang}",
            "link": 1,
            "date": 1,
            "popularity": 1,
        }

        project = await self.collection.find_one({"id": project_id}, projection)

        if project:
            if isinstance(project.get("title"), dict):
                project["title"] = project["title"].get(lang, "")
            if isinstance(project.get("description"), dict):
                project["description"] = project["description"].get(lang, "")

        return project

    async def get_projects_by_popularity(
        self,
        min_popularity: int,
        max_popularity: int,
        lang: str = "en",
        sort: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get projects within popularity range.

        Args:
            min_popularity (int): Minimum popularity value.
            max_popularity (int): Maximum popularity value.
            lang (str): Language code. Defaults to 'en'.
            sort (Optional[str]): Sorting option.

        Returns:
            List[Dict]: Filtered projects.
        """
        filter_query = {"popularity": {"$gte": min_popularity, "$lte": max_popularity}}
        projection = {
            "_id": 0,
            "id": 1,
            "title": f"$title.{lang}",
            "thumbnail": 1,
            "image": 1,
            "description": f"$description.{lang}",
            "link": 1,
            "date": 1,
            "popularity": 1,
        }

        sort_mapping = {
            "date_desc": [("date", -1)],
            "date_asc": [("date", 1)],
            "popularity_desc": [("popularity", -1)],
            "popularity_asc": [("popularity", 1)],
            None: None,
        }

        sort_criteria = sort_mapping.get(sort)

        if sort_criteria:
            cursor = self.collection.find(filter_query, projection).sort(sort_criteria)
        else:
            cursor = self.collection.find(filter_query, projection)

        projects = await cursor.to_list(length=None)

        for project in projects:
            if isinstance(project.get("title"), dict):
                project["title"] = project["title"].get(lang, "")
            if isinstance(project.get("description"), dict):
                project["description"] = project["description"].get(lang, "")

        return projects

    async def get_projects_by_year(
        self, year: int, lang: str = "en", sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get projects from specific year.

        Args:
            year (int): Year to filter by.
            lang (str): Language code. Defaults to 'en'.
            sort (Optional[str]): Sorting option.

        Returns:
            List[Dict]: Projects from specified year.
        """
        filter_query = {
            "date": {
                "$gte": f"{year}-01-01T00:00:00.000Z",
                "$lt": f"{year + 1}-01-01T00:00:00.000Z",
            }
        }

        projection = {
            "_id": 0,
            "id": 1,
            "title": f"$title.{lang}",
            "thumbnail": 1,
            "image": 1,
            "description": f"$description.{lang}",
            "link": 1,
            "date": 1,
            "popularity": 1,
        }

        sort_mapping = {
            "date_desc": [("date", -1)],
            "date_asc": [("date", 1)],
            "popularity_desc": [("popularity", -1)],
            "popularity_asc": [("popularity", 1)],
            None: None,
        }

        sort_criteria = sort_mapping.get(sort)

        if sort_criteria:
            cursor = self.collection.find(filter_query, projection).sort(sort_criteria)
        else:
            cursor = self.collection.find(filter_query, projection)

        projects = await cursor.to_list(length=None)

        for project in projects:
            if isinstance(project.get("title"), dict):
                project["title"] = project["title"].get(lang, "")
            if isinstance(project.get("description"), dict):
                project["description"] = project["description"].get(lang, "")

        return projects

    async def get_most_popular_projects(
        self, limit: int = 5, lang: str = "en"
    ) -> List[Dict[str, Any]]:
        """Get top N most popular projects.

        Args:
            limit (int): Number of projects to return. Defaults to 5.
            lang (str): Language code. Defaults to 'en'.

        Returns:
            List[Dict]: Most popular projects.
        """
        projection = {
            "_id": 0,
            "id": 1,
            "title": f"$title.{lang}",
            "thumbnail": 1,
            "image": 1,
            "description": f"$description.{lang}",
            "link": 1,
            "date": 1,
            "popularity": 1,
        }

        cursor = (
            self.collection.find({}, projection).sort("popularity", -1).limit(limit)
        )
        projects = await cursor.to_list(length=None)

        for project in projects:
            if isinstance(project.get("title"), dict):
                project["title"] = project["title"].get(lang, "")
            if isinstance(project.get("description"), dict):
                project["description"] = project["description"].get(lang, "")

        return projects

    async def get_recent_projects(
        self, limit: int = 5, lang: str = "en"
    ) -> List[Dict[str, Any]]:
        """Get most recent projects.

        Args:
            limit (int): Number of projects to return. Defaults to 5.
            lang (str): Language code. Defaults to 'en'.

        Returns:
            List[Dict]: Most recent projects.
        """
        projection = {
            "_id": 0,
            "id": 1,
            "title": f"$title.{lang}",
            "thumbnail": 1,
            "image": 1,
            "description": f"$description.{lang}",
            "link": 1,
            "date": 1,
            "popularity": 1,
        }

        cursor = self.collection.find({}, projection).sort("date", -1).limit(limit)
        projects = await cursor.to_list(length=None)

        for project in projects:
            if isinstance(project.get("title"), dict):
                project["title"] = project["title"].get(lang, "")
            if isinstance(project.get("description"), dict):
                project["description"] = project["description"].get(lang, "")

        return projects

    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project.

        Args:
            project_data (Dict): Project data including multilingual fields.

        Returns:
            Dict: Created project.
        """
        required_fields = [
            "id",
            "title",
            "thumbnail",
            "image",
            "description",
            "link",
            "date",
            "popularity",
        ]
        for field in required_fields:
            if field not in project_data:
                raise ValueError(f"Missing required field: {field}")

        # Проверяем, не существует ли уже проект с таким ID
        existing = await self.get_project_by_id(project_data["id"])
        if existing:
            raise ValueError(f"Project with ID '{project_data['id']}' already exists")

        result = await self.collection.insert_one(project_data)
        return await self.get_project_by_id(project_data["id"])
