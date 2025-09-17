import json
from pathlib import Path
from typing import Optional

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.topology import ServerSelectionTimeoutError
from pymongo.errors import ConnectionFailure, OperationFailure

from services.logger import get_logger
from settings import settings

logger = get_logger("db_connection")


class MongoConnectionManager:
    """
    Manages MongoDB connection operations
    including opening and closing connections.
    """

    def __init__(self, host: str) -> None:
        """Initializes the MongoDB connection manager.

        Args:
            host (str): MongoDB host connection string.
        """
        self.host = host
        self.client: Optional[AsyncMongoClient] = None

    async def open_connection(self) -> AsyncMongoClient:
        """
        Establishes a connection to MongoDB server.

        Creates an asynchronous MongoDB client and verifies the connection
        by sending a ping command to the admin database.

        Returns:
            AsyncMongoClient: Connected MongoDB client instance.

        Raises:
            OperationFailure: If MongoDB operation fails,
            including authentication errors.
            ConnectionFailure: If connection to MongoDB server fails.
            ServerSelectionTimeoutError: If server selection times out.
        """
        try:
            self.client = AsyncMongoClient(
                self.host,
                connectTimeoutMS=settings.MONGO_DB_CONNECTION_TIMEOUT_MS,
                serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
            )
            await self.client.admin.command("ping")
            logger.info("MongoDB connection successful")
            return self.client

        except OperationFailure as e:
            if "Authentication failed" in str(e):
                logger.exception(
                    "MongoDB authentication failed: invalid login or password"
                )
            else:
                logger.exception(f"MongoDB operation failed: {e}")
            raise
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.exception(f"MongoDB connection failed: {e}")
            raise

    async def close_connection(self):
        """
        Closes the MongoDB connection if it exists.

        Safely closes the client connection
        and sets the client reference to None.
        """
        if self.client:
            await self.client.close()


class MongoDatabaseManager:
    """
    Manages MongoDB database operations
    including existence checks and creation.
    """

    def __init__(self, client: AsyncMongoClient) -> None:
        """Initializes the MongoDB database manager.

        Args:
            client (AsyncMongoClient): Connected MongoDB client instance.
        """
        self.client = client

    async def check_database_existence(self, db_name: str) -> bool:
        """Checks if a database exists in the MongoDB instance.

        Args:
            db_name (str): Name of the database to check.

        Returns:
            bool: True if database exists, False otherwise.
        """
        try:
            databases = await self.client.list_database_names()

            if db_name in databases:
                logger.info(f"{db_name} is already in database")
                return True
            else:
                logger.warning(f"{db_name} not in database")
                return False

        except OperationFailure as e:
            logger.exception(f"Database check failed: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error during database check: {e}")
            return False

    async def create_database(self, db_name: str) -> AsyncDatabase:
        """Creates a new database if it doesn't exist.

        Args:
            db_name (str): Name of the database to create.

        Returns:
            AsyncDatabase: Created database instance if successful,
            False otherwise.

        Raises:
            OperationFailure: If MongoDB operation fails
            during database creation.
            Exception: For any unexpected errors during database creation.
        """
        try:
            self.db = self.client[db_name]
            await self.db.command("ping")
            logger.info(f"Database '{db_name}' created successfully")
            return self.db

        except OperationFailure as e:
            logger.exception(f"Failed to create database: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error creating database: {e}")
            return False


class MongoCollectionsManager:
    """
    Manages MongoDB collection operations
    including existence checks and data initialization.
    """

    def __init__(self, client: AsyncMongoClient, db: AsyncDatabase) -> None:
        """Initializes the MongoDB collections manager.

        Args:
            client (AsyncMongoClient): Connected MongoDB client instance.
            db (AsyncDatabase): Target database for collection operations.
        """
        self.client = client
        self.db = db
        self.collection_paths: dict[str, Path] = {
            "about": settings.PATH_ABOUT_JSON,
            "tech": settings.PATH_TECH_JSON,
            "projects": settings.PATH_PROJECTS_JSON,
            "certificates": settings.PATH_CERTIFICATES_JSON,
            "publications": settings.PATH_PUBLICATIONS_JSON,
        }

    async def collection_exists(self, collection_name: str) -> bool:
        """Checks if a collection exists in the current database.

        Args:
            collection_name (str): Name of the collection to check.

        Returns:
            bool: True if collection exists, False otherwise.
        """
        collections = await self.db.list_collection_names()
        if collection_name in collections:
            logger.info(f"Collection {collection_name} already exists")
            return True
        else:
            logger.warning(f"Collection {collection_name} doesnt exist")
            return False

    async def initialize_collections(self) -> None:
        """Initializes all collections with initial data from JSON files.

        Raises:
            Exception: If any error occurs during collection initialization.
        """
        try:
            for collection_name, file_path in self.collection_paths.items():
                if await self.collection_exists(collection_name):
                    continue

                await self.load_and_insert_data(
                    file_path, self.db[collection_name], logger
                )
                logger.info(
                    f"Collection {collection_name} initialized successfully"
                )

            logger.info("All collections initialized successfully")

        except Exception as e:
            logger.exception(f"Failed to initialize collections: {e}")
            raise

    @staticmethod
    async def load_and_insert_data(file_path: Path, collection, logger):
        """Loads data from JSON file
        and inserts it into the specified collection.

        Args:
            file_path (Path): Path to the JSON file containing data.
            collection: MongoDB collection instance
            where data will be inserted.
            logger: Logger instance for logging operations.

        Raises:
            Exception: If any error occurs
            during file loading or data insertion.
        """
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        await collection.insert_many(data)
                        logger.info(
                            f"Data loaded from {file_path.name} ({len(data)} documents)"
                        )
                    else:
                        logger.warning(f"File {file_path.name} is empty")
            else:
                logger.warning(f"File {file_path} not found")
        except json.JSONDecodeError as e:
            logger.exception(f"Invalid JSON in {file_path}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Error loading {file_path}: {e}")
            raise
