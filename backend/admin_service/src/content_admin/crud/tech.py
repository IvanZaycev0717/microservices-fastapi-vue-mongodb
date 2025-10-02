from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from content_admin.models.tech import TechResponse
from services.logger import get_logger
from settings import settings

logger = get_logger(settings.CONTENT_ADMIN_TECH_NAME)


class TechCRUD:
    """Handles technology database operations.

    Attributes:
        collection: MongoDB collection instance for technology data.
    """

    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.tech

    # READ
    async def read_all(self) -> list[TechResponse]:
        """Retrieve all technologies from the database.

        Returns:
            list[TechResponse]: List of technology response models.
        """
        cursor = self.collection.find()
        results = await cursor.to_list(length=None)
        return [TechResponse(**doc) for doc in results]

    # UPDATE
    async def update_kingdom_items(
        self, kingdom_name: str, items: list[str]
    ) -> bool:
        """Update items for a specific kingdom.

        Args:
            kingdom_name (str): Name of the kingdom to update.
            items (list[str]): List of items to set for the kingdom.

        Returns:
            bool: True if update was acknowledged by database, False otherwise.
        """
        result = await self.collection.update_one(
            {}, {"$set": {f"{kingdom_name}.items": items}}
        )
        return result.acknowledged
