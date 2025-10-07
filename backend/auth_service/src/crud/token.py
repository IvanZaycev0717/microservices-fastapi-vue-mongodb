from datetime import datetime

from pymongo.asynchronous.database import AsyncDatabase


class TokenCRUD:
    """Handles refresh token database operations."""

    def __init__(self, db: AsyncDatabase):
        self.collection = db.tokens

    async def create_refresh_token(
        self,
        user_id: str,
        token: str,
        expired_at: datetime,
        used: bool = False,
    ) -> str:
        """Create a new refresh token in the database."""
        token_data = {
            "user_id": user_id,
            "token": token,
            "expired_at": expired_at,
            "used": used,
            "created_at": datetime.now(),
        }
        result = await self.collection.insert_one(token_data)
        return str(result.inserted_id)

    async def get_refresh_token(self, token: str) -> dict | None:
        """Retrieve an unused refresh token from the database."""
        return await self.collection.find_one({"token": token, "used": False})

    async def mark_token_as_used(self, token: str) -> bool:
        """Mark a refresh token as used in the database."""
        result = await self.collection.update_one(
            {"token": token, "used": False},
            {"$set": {"used": True, "used_at": datetime.now()}},
        )
        return result.modified_count > 0

    async def invalidate_user_tokens(self, user_id: str) -> int:
        """Invalidate all unused refresh tokens for a specific user."""
        result = await self.collection.update_many(
            {"user_id": user_id, "used": False},
            {"$set": {"used": True, "invalidated_at": datetime.now()}},
        )
        return result.modified_count
