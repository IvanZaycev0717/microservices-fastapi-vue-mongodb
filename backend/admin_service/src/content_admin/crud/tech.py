from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from content_admin.models.tech import TechResponse
from services.logger import get_logger
from settings import settings

logger = get_logger(settings.CONTENT_ADMIN_TECH_NAME)


class TechCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.tech

    # READ
    async def read_all(self) -> list[TechResponse]:
        cursor = self.collection.find()
        results = await cursor.to_list(length=None)
        return [TechResponse(**doc) for doc in results]

    # UPDATE
    async def update_kingdom_items(
        self, kingdom_name: str, items: list[str]
    ) -> bool:
        result = await self.collection.update_one(
            {}, {"$set": {f"{kingdom_name}.items": items}}
        )
        return result.acknowledged
