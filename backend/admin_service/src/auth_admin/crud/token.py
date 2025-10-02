# crud/token.py
from datetime import datetime

from pymongo.asynchronous.database import AsyncDatabase


class TokenCRUD:
    """Handles refresh token database operations.

    Attributes:
        collection: MongoDB collection instance for token data.
    """

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
        """Create a new refresh token in the database.

        Args:
            user_id (str): ID of the user associated with the token.
            token (str): The refresh token string.
            expired_at (datetime): Expiration datetime of the token.
            used (bool, optional): Whether the token has been used. Defaults to False.

        Returns:
            ObjectId: The inserted document's ID.
        """
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
        """Retrieve an unused refresh token from the database.

        Args:
            token (str): The refresh token string to search for.

        Returns:
            dict: Token document if found and unused, None otherwise.
        """
        return await self.collection.find_one({"token": token, "used": False})

    async def get_user_refresh_tokens(self, user_id: str):
        """Retrieve all unused refresh tokens for a specific user.

        Args:
            user_id (str): ID of the user to retrieve tokens for.

        Returns:
            list: List of unused refresh token documents for the user.
        """
        cursor = self.collection.find({"user_id": user_id, "used": False})
        return await cursor.to_list(length=None)

    # UPDATE
    async def mark_token_as_used(self, token: str) -> bool:
        """Mark a refresh token as used in the database.

        Args:
            token (str): The refresh token string to mark as used.

        Returns:
            bool: True if token was successfully updated, False otherwise.
        """
        result = await self.collection.update_one(
            {"token": token, "used": False},
            {"$set": {"used": True, "used_at": datetime.now()}},
        )
        return result.modified_count > 0

    async def invalidate_user_tokens(self, user_id: str) -> int:
        """Invalidate all unused refresh tokens for a specific user.

        Args:
            user_id (str): ID of the user whose tokens should be invalidated.

        Returns:
            int: Number of tokens that were invalidated.
        """
        result = await self.collection.update_many(
            {"user_id": user_id, "used": False},
            {"$set": {"used": True, "invalidated_at": datetime.now()}},
        )
        return result.modified_count

    # DELETE
    async def delete_expired_tokens(self) -> int:
        """Delete all expired tokens from the database.

        Returns:
            int: Number of tokens that were deleted.
        """
        result = await self.collection.delete_many(
            {"expired_at": {"$lt": datetime.now()}}
        )
        return result.deleted_count
