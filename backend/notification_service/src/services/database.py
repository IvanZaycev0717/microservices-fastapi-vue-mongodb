from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from crud.notification import NotificationCRUD
from logger import get_logger
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

        Creates MongoDB client using secret URL, selects database, and verifies
        connection with a ping command.

        Raises:
            Exception: If connection to MongoDB fails or ping command times out.

        Note:
            - Uses secret MongoDB URL from application settings
            - Applies timeout settings for connection and server selection
            - Verifies connection with ping command before proceeding
        """
        try:
            self.client = AsyncMongoClient(
                settings.NOTIFICATION_SERVICE_MONGODB_URL.get_secret_value(),
                connectTimeoutMS=settings.MONGO_CONNECTION_TIMEOUT_MS,
                serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
            )
            self.db = self.client[
                settings.NOTIFICATION_SERVICE_MONGO_DATABASE_NAME
            ]
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

    def get_notification_crud(self) -> NotificationCRUD:
        """Creates and returns a NotificationCRUD instance.

        Returns:
            NotificationCRUD: CRUD operations instance for notification data.

        Note:
            - Provides access to notification-specific database operations
            - Requires database connection to be established first
        """
        return NotificationCRUD(self.db)


db_manager = DatabaseManager()
