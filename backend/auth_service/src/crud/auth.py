from datetime import datetime

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from models.schemas import UserDB


class AuthCRUD:
    """Data access layer for authentication-related database operations.

    Handles CRUD operations for user authentication data including
    user management and password operations.

    Attributes:
        collection: MongoDB users collection instance for user data operations.
    """

    def __init__(self, db: AsyncDatabase):
        self.collection = db.users

    async def create_user(
        self, email: str, password_hash: str, roles: list[str] | None = None
    ) -> UserDB:
        """Create a new user in the database.

        Inserts a new user document with the provided credentials and default
        attributes, then returns the created user object.

        Args:
            email: User's email address.
            password_hash: Hashed password string.
            roles: List of user roles. Defaults to ["user"] if not provided.

        Returns:
            UserDB: The created user object with generated ID.

        Note:
            - Sets default role as "user" if no roles provided
            - Initializes user as not banned and with creation timestamp
            - Converts MongoDB ObjectId to string ID in response
        """
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
        """Retrieve a user from the database by email address.

        Args:
            email: Email address to search for.

        Returns:
            UserDB | None: User object if found, None otherwise.

        Note:
            - Performs case-sensitive email lookup
            - Converts MongoDB ObjectId to string ID in response
        """
        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            del user_dict["_id"]
            return UserDB(**user_dict)
        return None

    async def get_user_by_id(self, user_id: str) -> UserDB | None:
        """Retrieve a user from the database by user ID.

        Args:
            user_id: String representation of user's ObjectId.

        Returns:
            UserDB | None: User object if found, None otherwise.

        Note:
            - Converts string ID to ObjectId for MongoDB query
            - Returns None if user not found or invalid ID format
        """
        user_dict = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            del user_dict["_id"]
            return UserDB(**user_dict)
        return None

    async def update_user_last_login(self, email: str) -> UserDB | None:
        """Update user's last login timestamp.

        Args:
            email: Email address of the user to update.

        Returns:
            UserDB | None: Updated user object if found and modified, None otherwise.

        Note:
            - Sets last_login_at to current datetime
            - Returns the updated user object for convenience
        """
        result = await self.collection.update_one(
            {"email": email}, {"$set": {"last_login_at": datetime.now()}}
        )
        if result.modified_count > 0:
            return await self.get_user_by_email(email)
        return None

    async def update_user_password(
        self, user_id: str, new_password_hash: str
    ) -> bool:
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
                {"$set": {"password_hash": new_password_hash}},
            )
            return result.modified_count > 0
        except Exception:
            return False
