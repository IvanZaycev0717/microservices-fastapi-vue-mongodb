from datetime import datetime

from pymongo.asynchronous.database import AsyncDatabase


class TokenCRUD:
    """Data access layer for token-related database operations.

    Handles CRUD operations for authentication tokens including
    refresh tokens and reset tokens.

    Attributes:
        collection: MongoDB tokens collection instance for token data operations.
    """

    def __init__(self, db: AsyncDatabase):
        self.collection = db.tokens

    async def create_refresh_token(
        self,
        user_id: str,
        token: str,
        expired_at: datetime,
        used: bool = False,
    ) -> str:
        """Store a new refresh token in the database.

        Args:
            user_id: ID of the user associated with the token.
            token: The refresh token string to store.
            expired_at: Datetime when the token expires.
            used: Whether the token has been used. Defaults to False.

        Returns:
            str: The ID of the created token document.

        Note:
            - Sets creation timestamp automatically
            - Stores token with expiration for automatic cleanup
        """
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
        """Retrieve an unused refresh token from the database.

        Args:
            token: The refresh token string to look up.

        Returns:
            dict | None: Token document if found and not used, None otherwise.

        Note:
            - Only returns tokens that haven't been marked as used
            - Returns raw MongoDB document for flexibility
        """
        return await self.collection.find_one({"token": token, "used": False})

    async def mark_token_as_used(self, token: str) -> bool:
        """Mark a refresh token as used to prevent reuse.

        Args:
            token: The refresh token string to mark as used.

        Returns:
            bool: True if token was found and updated, False otherwise.

        Note:
            - Only marks tokens that are currently unused
            - Sets used_at timestamp to current datetime
            - Prevents token replay attacks by marking as used
        """
        result = await self.collection.update_one(
            {"token": token, "used": False},
            {"$set": {"used": True, "used_at": datetime.now()}},
        )
        return result.modified_count > 0

    async def invalidate_user_tokens(self, user_id: str) -> int:
        """Invalidate all unused tokens for a specific user.

        Args:
            user_id: ID of the user whose tokens should be invalidated.

        Returns:
            int: Number of tokens that were invalidated.

        Note:
            - Marks all unused tokens for the user as used
            - Sets invalidation timestamp for audit purposes
            - Useful for security measures like password changes or account suspension
        """
        result = await self.collection.update_many(
            {"user_id": user_id, "used": False},
            {"$set": {"used": True, "invalidated_at": datetime.now()}},
        )
        return result.modified_count
