from typing import List

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

logger = get_logger("Database")


class DatabaseManager:
    """Manages MongoDB database connections and provides database access.

    This class handles connection lifecycle and provides access to
    database collections through a centralized interface.

    Attributes:
        client: MongoDB async client instance.
        db: MongoDB async database instance.
    """

    def __init__(self) -> None:
        self.client: AsyncMongoClient | None = None
        self.db: AsyncDatabase | None = None

    async def connect(self) -> None:
        """Establishes connection to MongoDB database.

        Creates MongoDB client, selects database, and verifies connection
        with a ping command.

        Raises:
            Exception: If connection to MongoDB fails or ping command times out.

        Note:
            - Uses connection settings from application configuration
            - Applies timeout settings for connection and server selection
            - Verifies connection with ping command before proceeding
        """
        try:
            self.client = AsyncMongoClient(
                settings.GRPC_CONTENT_MONGODB_URL,
                connectTimeoutMS=settings.MONGO_CONNECTION_TIMEOUT_MS,
                serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
            )
            self.db = self.client[settings.GRPC_CONTENT_MONGODB_DB_NAME]
            await self.db.command("ping")
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self) -> None:
        """Closes the MongoDB connection.

        Safely closes the database client connection if it exists.

        Note:
            - Idempotent operation - safe to call multiple times
            - Logs connection closure for monitoring purposes
        """
        if self.client is not None:
            await self.client.close()
            logger.info("MongoDB connection closed")

    async def get_about(self, lang: str | None = None) -> List[AboutDocument]:
        """Retrieves about section documents with optional language filtering.

        Fetches about documents from the database, with support for filtering
        by language and projecting only relevant translation fields.

        Args:
            lang: Language code to filter translations ('en' or 'ru').
                If None or invalid, returns all documents with full translations.

        Returns:
            List[AboutDocument]: List of about documents with requested translations.

        Raises:
            RuntimeError: If database connection is not established.

        Note:
            - Uses aggregation pipeline for language-specific projection
            - Returns all languages if no valid language specified
            - Converts MongoDB documents to Pydantic models
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
        """Retrieves all technology stack documents.

        Fetches all technology documents from the database without filtering.

        Returns:
            List[TechDocument]: List of all technology documents.

        Raises:
            RuntimeError: If database connection is not established.

        Note:
            - Returns all documents in the tech collection
            - Converts MongoDB documents to Pydantic models
        """
        if self.db is None:
            raise RuntimeError("Database not connected")

        cursor = self.db.tech.find()
        documents = await cursor.to_list(length=None)
        return [TechDocument(**doc) for doc in documents]

    async def get_projects(
        self, lang: str = "en", sort: str = "date_desc"
    ) -> list[ProjectDocument]:
        """Retrieves projects with language-specific content and sorting options.

        Fetches projects from database with support for multiple languages
        and customizable sorting by date or popularity.

        Args:
            lang: Language code for translations ('en' or 'ru'). Defaults to 'en'.
            sort: Sorting preference. Options: 'date_desc', 'date_asc',
                'popularity_desc', 'popularity_asc'. Defaults to 'date_desc'.

        Returns:
            list[ProjectDocument]: List of projects with requested language
            and sorting applied.

        Raises:
            RuntimeError: If database connection is not established.

        Note:
            - Supports English and Russian language translations
            - Handles both datetime objects and string dates
            - Returns empty strings for missing translations
            - Converts MongoDB ObjectId to string ID
        """
        if sort.startswith("date"):
            sort_field = "date"
            sort_direction = DESCENDING if sort.endswith("desc") else ASCENDING
        else:
            sort_field = "popularity"
            sort_direction = DESCENDING

        cursor = self.db.projects.find({}).sort(sort_field, sort_direction)
        results = await cursor.to_list(length=None)

        transformed_results = []
        for item in results:
            if lang not in ("en", "ru"):
                transformed_results.append(
                    {
                        "id": str(item["_id"]),
                        "title": item["title"],
                        "thumbnail": item["thumbnail"],
                        "image": item["image"],
                        "description": item["description"],
                        "link": item["link"],
                        "date": item["date"].isoformat()
                        if hasattr(item["date"], "isoformat")
                        else item["date"],
                        "popularity": item["popularity"],
                    }
                )
            else:
                transformed_results.append(
                    {
                        "id": str(item["_id"]),
                        "title": item["title"].get(lang, ""),
                        "thumbnail": item["thumbnail"],
                        "image": item["image"],
                        "description": item["description"].get(lang, ""),
                        "link": item["link"],
                        "date": item["date"].isoformat()
                        if hasattr(item["date"], "isoformat")
                        else item["date"],
                        "popularity": item["popularity"],
                    }
                )
        return transformed_results

    async def get_certificates(
        self, sort: str = "date_desc"
    ) -> List[CertificateDocument]:
        """Retrieves certificates with customizable sorting.

        Fetches certificate documents from the database with options to sort
        by date or popularity in ascending or descending order.

        Args:
            sort: Sorting preference. Options: 'date_desc', 'date_asc',
                'popularity_desc', 'popularity_asc'. Defaults to 'date_desc'.

        Returns:
            List[CertificateDocument]: List of certificates with requested sorting.

        Raises:
            RuntimeError: If database connection is not established.

        Note:
            - Sorts by date or popularity field as specified
            - Defaults to descending order for both date and popularity
            - Converts MongoDB documents to Pydantic models
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
        """Retrieves publications with language-specific titles and sorting.

        Fetches publication documents with support for language-specific titles
        and customizable sorting by date or rating.

        Args:
            lang: Language code for title translation ('en' or 'ru').
            sort: Sorting preference. Options: 'date_desc', 'date_asc',
                'rating_desc', 'rating_asc'. Defaults to 'date_desc'.

        Returns:
            List[PublicationDocument]: List of publications with requested
            language and sorting applied.

        Raises:
            RuntimeError: If database connection is not established.

        Note:
            - Extracts language-specific title from nested dictionary
            - Returns empty string if translation for specified language is missing
            - Sorts by date or rating field as specified
            - Converts MongoDB documents to Pydantic models
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


db_manager = DatabaseManager()
