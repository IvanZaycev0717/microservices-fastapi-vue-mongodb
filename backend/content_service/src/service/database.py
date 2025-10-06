from typing import List

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from logger import get_logger
from models.schemas import (
    AboutDocument,
    CertificateDocument,
    ProjectDocument,
    PublicationDocument,
    TechDocument,
)
from settings import settings

logger = get_logger("database")


class DatabaseManager:
    """Manages MongoDB database connections and operations.

    Attributes:
        client: Async MongoDB client instance.
        db: Async MongoDB database instance.
    """

    def __init__(self) -> None:
        """Initializes the database manager with connection settings."""
        self.client: AsyncMongoClient | None = None
        self.db: AsyncDatabase | None = None

    async def connect(self) -> None:
        """Establishes connection to MongoDB database."""
        try:
            self.client = AsyncMongoClient(
                settings.MONGODB_URL,
                connectTimeoutMS=settings.MONGO_CONNECTION_TIMEOUT_MS,
                serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
            )
            self.db = self.client[settings.MONGODB_DB_NAME]
            await self.db.command("ping")
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self) -> None:
        """Closes the MongoDB connection."""
        if self.client is not None:
            await self.client.close()
            logger.info("MongoDB connection closed")

    async def get_about(self, lang: str | None = None) -> List[AboutDocument]:
        """Retrieves about documents with optional language filtering.

        Args:
            lang: Language code for filtering translations.

        Returns:
            List of about documents.

        Raises:
            Exception: If database operation fails.
        """
        if self.db is None:
            raise RuntimeError("Database not connected")

        if not lang or lang not in ("en", "ru"):
            cursor = self.db.about.find()
            documents = await cursor.to_list(length=None)
            return [AboutDocument(**doc) for doc in documents]
        else:
            pipeline = [
                {
                    "$project": {
                        "image_url": 1,
                        "translations": {lang: f"$translations.{lang}"},
                        "_id": 1,
                    }
                }
            ]
            cursor = await self.db.about.aggregate(pipeline)
            documents = await cursor.to_list(length=None)
            return [AboutDocument(**doc) for doc in documents]

    async def get_tech(self) -> List[TechDocument]:
        """Retrieves all technology documents.

        Returns:
            List of technology documents.

        Raises:
            Exception: If database operation fails.
        """
        if self.db is None:
            raise RuntimeError("Database not connected")

        cursor = self.db.tech.find()
        documents = await cursor.to_list(length=None)
        return [TechDocument(**doc) for doc in documents]

    async def get_projects(
        self, lang: str, sort: str = "date_desc"
    ) -> List[ProjectDocument]:
        """Retrieves projects with language and sorting options.

        Args:
            lang: Language code for project data.
            sort: Sorting criteria.

        Returns:
            List of project documents.

        Raises:
            Exception: If database operation fails.
        """
        if self.db is None:
            raise RuntimeError("Database not connected")

        if sort.startswith("date"):
            sort_field = "date"
            sort_direction = DESCENDING if sort.endswith("desc") else ASCENDING
        else:
            sort_field = "popularity"
            sort_direction = DESCENDING

        cursor = self.db.projects.find({}).sort(sort_field, sort_direction)
        documents = await cursor.to_list(length=None)

        project_docs = []
        for doc in documents:
            project_data = dict(doc)

            if lang in ("en", "ru"):
                if "title" in project_data and isinstance(
                    project_data["title"], dict
                ):
                    project_data["title"] = project_data["title"].get(lang, "")
                if "description" in project_data and isinstance(
                    project_data["description"], dict
                ):
                    project_data["description"] = project_data[
                        "description"
                    ].get(lang, "")

            project_docs.append(ProjectDocument(**project_data))

        return project_docs

    async def get_certificates(
        self, sort: str = "date_desc"
    ) -> List[CertificateDocument]:
        """Retrieves certificates with sorting options.

        Args:
            sort: Sorting criteria.

        Returns:
            List of certificate documents.

        Raises:
            Exception: If database operation fails.
        """
        if self.db is None:
            raise RuntimeError("Database not connected")

        if sort.startswith("date"):
            sort_field = "date"
            sort_direction = DESCENDING if sort.endswith("desc") else ASCENDING
        else:
            sort_field = "popularity"
            sort_direction = DESCENDING

        cursor = self.db.certificates.find({}).sort(sort_field, sort_direction)
        documents = await cursor.to_list(length=None)
        return [CertificateDocument(**doc) for doc in documents]

    async def get_publications(
        self, lang: str, sort: str = "date_desc"
    ) -> List[PublicationDocument]:
        """Retrieves publications with language and sorting options.

        Args:
            lang: Language code for publication data.
            sort: Sorting criteria.

        Returns:
            List of publication documents.

        Raises:
            Exception: If database operation fails.
        """
        if self.db is None:
            raise RuntimeError("Database not connected")

        if sort.startswith("date"):
            sort_field = "date"
            sort_direction = DESCENDING if sort.endswith("desc") else ASCENDING
        else:
            sort_field = "rating"
            sort_direction = DESCENDING

        cursor = self.db.publications.find({}).sort(sort_field, sort_direction)
        documents = await cursor.to_list(length=None)

        publication_docs = []
        for doc in documents:
            publication_data = dict(doc)

            if lang in ("en", "ru"):
                if "title" in publication_data and isinstance(
                    publication_data["title"], dict
                ):
                    publication_data["title"] = publication_data["title"].get(
                        lang, ""
                    )

            publication_docs.append(PublicationDocument(**publication_data))

        return publication_docs


# Global database instance
db_manager = DatabaseManager()
