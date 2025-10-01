from datetime import datetime
from typing import Optional

from pymongo.asynchronous.database import AsyncDatabase

from auth_admin.models.auth import UserDB
from auth_admin.models.user_role import UserRole


class AuthCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection = db.users

    # CREATE
    async def create_user(
        self, email: str, password_hash: str, roles: list[UserRole]
    ) -> UserDB:
        """Create user and return as UserDB model."""
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "roles": [role.value for role in roles]
            if roles
            else [UserRole.USER.value],
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

    # READ
    async def get_user_by_email(self, email: str) -> Optional[UserDB]:
        """Get user by email and return as UserDB model."""
        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            del user_dict["_id"]
            return UserDB(**user_dict)
        return None

    async def get_all_users(self) -> list[UserDB]:
        cursor = self.collection.find()
        users_dict = await cursor.to_list(length=None)

        users = []
        for user_dict in users_dict:
            user_dict["id"] = str(user_dict["_id"])
            del user_dict["_id"]
            users.append(UserDB(**user_dict))

        return users

    # UPDATE
    async def update_user(
        self, email: str, update_data: dict
    ) -> Optional[UserDB]:
        result = await self.collection.update_one(
            {"email": email}, {"$set": update_data}
        )

        if result.modified_count > 0:
            updated_user = await self.collection.find_one({"email": email})
            if updated_user:
                updated_user["id"] = str(updated_user["_id"])
                del updated_user["_id"]
                return UserDB(**updated_user)
        return None

    async def update_user_last_login(self, email: str) -> Optional[UserDB]:
        """Update user's last login time and return UserDB model."""
        return await self.update_user(email, {"last_login_at": datetime.now()})

    # DELETE
    async def delete_user_by_email(self, email: str) -> bool:
        """Delete user by email."""
        result = await self.collection.delete_one({"email": email})
        return result.deleted_count > 0
