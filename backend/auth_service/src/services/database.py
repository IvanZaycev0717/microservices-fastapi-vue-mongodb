from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from crud.auth import AuthCRUD
from crud.token import TokenCRUD
from logger import get_logger
from settings import settings

logger = get_logger("Database")


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
                settings.GRPC_AUTH_MONGODB_URL.get_secret_value(),
                connectTimeoutMS=settings.MONGO_CONNECTION_TIMEOUT_MS,
                serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
            )
            self.db = self.client[settings.GRPC_AUTH_MONGODB_DB_NAME]
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

    def get_auth_crud(self):
        """Get AuthCRUD instance for user operations."""
        return AuthCRUD(self.db)

    def get_token_crud(self):
        """Get TokenCRUD instance for token operations."""
        return TokenCRUD(self.db)


db_manager = DatabaseManager()
