from datetime import datetime

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from models.schemas import UserDB


class AuthCRUD:
    """Handles authentication-related database operations."""

    def __init__(self, db: AsyncDatabase):
        self.collection = db.users

    async def create_user(
        self, email: str, password_hash: str, roles: list[str] | None = None
    ) -> UserDB:
        """Create a new user in the database."""
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "roles": roles or ["user"],
            "is_banned": False,
            "created_at": datetime.now(),
            "last_login_at": None,
        }

        result = await self.collection.insert_one(user_data)
        created_user = await self.collection.find_one(
            {"_id": result.inserted_id}
        )
        created_user["id"] = str(created_user["_id"])
        del created_user["_id"]
        return UserDB(**created_user)

    async def get_user_by_email(self, email: str) -> UserDB | None:
        """Retrieve a user from the database by email address."""
        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            del user_dict["_id"]
            return UserDB(**user_dict)
        return None

    async def get_user_by_id(self, user_id: str) -> UserDB | None:
        """Retrieve a user from the database by ID."""
        user_dict = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            del user_dict["_id"]
            return UserDB(**user_dict)
        return None

    async def update_user_last_login(self, email: str) -> UserDB | None:
        """Update user's last login timestamp."""
        result = await self.collection.update_one(
            {"email": email}, {"$set": {"last_login_at": datetime.now()}}
        )
        if result.modified_count > 0:
            return await self.get_user_by_email(email)
        return None

    async def update_user_password(self, user_id: str, new_password_hash: str) -> bool:
        """Update user's password hash.
        
        Args:
            user_id: User ID
            new_password_hash: New hashed password
            
        Returns:
            bool: True if password was updated successfully, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password_hash": new_password_hash}}
            )
            return result.modified_count > 0
        except Exception:
            return False