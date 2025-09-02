from typing import List, Optional, Dict, Any
from pymongo.asynchronous.collection import AsyncCollection


class BaseCRUD:
    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def create(self, document: Dict[str, Any]) -> Any:
        result = await self.collection.insert_one(document)
        return await self.get_by_id(result.inserted_id)

    async def get_by_id(self, id: Any) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": id})

    async def get_all(self, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        cursor = self.collection.find(filter or {})
        return await cursor.to_list(length=None)

    async def update(
        self, id: Any, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        result = await self.collection.update_one({"_id": id}, {"$set": update_data})
        if result.modified_count:
            return await self.get_by_id(id)
        return None

    async def delete(self, id: Any) -> bool:
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
