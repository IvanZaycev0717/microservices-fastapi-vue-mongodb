from datetime import datetime
from enum import Enum

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class AuthCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection = db.users

    # CREATE
    async def create_user(
        self,
        email: str,
        password_hash: str,
        roles: list[UserRole] | None = None,
    ) -> dict:
        """Create new user in database."""
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "is_banned": False,
            "roles": [role.value for role in (roles or [UserRole.USER])],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "last_login_at": None,
        }

        result = await self.collection.insert_one(user_data)
        return await self.get_user_by_id(result.inserted_id)

    # READ
    async def get_all_users(self) -> list[dict]:
        """Get all users from database."""
        cursor = self.collection.find()
        return await cursor.to_list()

    async def get_user_by_id(self, user_id: str) -> dict | None:
        """Get user by MongoDB ObjectId."""
        return await self.collection.find_one({"_id": ObjectId(user_id)})

    async def get_user_by_email(self, email: str) -> dict | None:
        """Get user by email address."""
        return await self.collection.find_one({"email": email})

    # UPDATE
    async def update_user_last_login(self, email: str) -> dict | None:
        """Update user's last login timestamp."""
        return await self.collection.find_one_and_update(
            {"email": email},
            {"$set": {"last_login_at": datetime.now()}},
            return_document=ReturnDocument.AFTER,
        )

    async def update_user(self, email: str, update_data: dict) -> dict | None:
        """Update user fields (is_banned, roles)."""
        allowed_fields = {"is_banned", "roles"}
        filtered_update = {
            key: value
            for key, value in update_data.items()
            if key in allowed_fields and value is not None
        }

        if not filtered_update:
            return None

        filtered_update["updated_at"] = datetime.now()

        return await self.collection.find_one_and_update(
            {"email": email},
            {"$set": filtered_update},
            return_document=ReturnDocument.AFTER,
        )

    # DELETE
    async def delete_user_by_email(self, email: str) -> bool:
        """Delete user by email address."""
        result = await self.collection.delete_one({"email": email})
        return result.deleted_count > 0
