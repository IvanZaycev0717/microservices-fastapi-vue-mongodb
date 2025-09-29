# crud/token.py
from datetime import datetime

from pymongo.asynchronous.database import AsyncDatabase


class TokenCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection = db.tokens

    # CREATE
    async def create_refresh_token(
        self,
        user_id: str,
        token: str,
        expired_at: datetime,
        used: bool = False,
    ):
        token_data = {
            "user_id": user_id,
            "token": token,
            "expired_at": expired_at,
            "used": used,
            "created_at": datetime.now(),
        }
        result = await self.collection.insert_one(token_data)
        return result.inserted_id

    # READ
    async def get_refresh_token(self, token: str):
        return await self.collection.find_one({"token": token, "used": False})

    async def get_user_refresh_tokens(self, user_id: str):
        cursor = self.collection.find({"user_id": user_id, "used": False})
        return await cursor.to_list(length=None)

    # UPDATE
    async def mark_token_as_used(self, token: str):
        result = await self.collection.update_one(
            {"token": token, "used": False},
            {"$set": {"used": True, "used_at": datetime.now()}},
        )
        return result.modified_count > 0

    async def invalidate_user_tokens(self, user_id: str):
        result = await self.collection.update_many(
            {"user_id": user_id, "used": False},
            {"$set": {"used": True, "invalidated_at": datetime.now()}},
        )
        return result.modified_count

    # DELETE
    async def delete_expired_tokens(self):
        result = await self.collection.delete_many(
            {"expired_at": {"$lt": datetime.now()}}
        )
        return result.deleted_count
