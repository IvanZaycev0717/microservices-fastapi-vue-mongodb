from datetime import datetime
from typing import Optional

from pymongo.asynchronous.database import AsyncDatabase

from auth_admin.models.auth import UserDB
from auth_admin.models.user_role import UserRole


class AuthCRUD:
    """Handles authentication-related database operations.

    Attributes:
        collection: MongoDB collection instance for user data.
    """

    def __init__(self, db: AsyncDatabase):
        self.collection = db.users

    # CREATE
    async def create_user(
        self, email: str, password_hash: str, roles: list[UserRole]
    ) -> UserDB:
        """Create a new user in the database.

        Args:
            email (str): User's email address.
            password_hash (str): Hashed password for the user.
            roles (list[UserRole]): List of roles assigned to the user.

        Returns:
            UserDB: User database model instance representing the created user.

        Note:
            If no roles are provided, defaults to [UserRole.USER].
            Sets initial user state with is_banned=False and created_at timestamp.
        """
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
        """Retrieve a user from the database by email address.

        Args:
            email (str): Email address to search for.

        Returns:
            Optional[UserDB]: User database model if found, None otherwise.
        """
        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            del user_dict["_id"]
            return UserDB(**user_dict)
        return None

    async def get_all_users(self) -> list[UserDB]:
        """Retrieve all users from the database.

        Returns:
            list[UserDB]: List of UserDB models representing all users in the database.
        """
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
        """Update user data in the database.

        Args:
            email (str): Email of the user to update.
            update_data (dict): Dictionary containing fields to update.

        Returns:
            Optional[UserDB]: Updated UserDB model if successful, None otherwise.
        """
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
        """Update user's last login timestamp.

        Args:
            email (str): Email of the user to update.

        Returns:
            Optional[UserDB]: Updated UserDB model if successful, None otherwise.
        """
        return await self.update_user(email, {"last_login_at": datetime.now()})

    # DELETE
    async def delete_user_by_email(self, email: str) -> bool:
        """Delete a user from the database by email.

        Args:
            email (str): Email of the user to delete.

        Returns:
            bool: True if user was successfully deleted, False otherwise.
        """
        result = await self.collection.delete_one({"email": email})
        return result.deleted_count > 0
