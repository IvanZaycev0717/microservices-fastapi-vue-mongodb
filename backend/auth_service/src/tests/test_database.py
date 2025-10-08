from unittest.mock import AsyncMock

from services.database import db_manager
import datetime


class TestDatabase:
    """Test database operations with mocked MongoDB."""

    async def test_get_user_by_email(self):
        mock_data = {
            "_id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "roles": ["user"],
            "is_banned": False,
            "created_at": "2024-01-01T00:00:00",
            "last_login_at": None,
        }

        db_manager.db.users.find_one = AsyncMock(return_value=mock_data)

        result = await db_manager.get_auth_crud().get_user_by_email(
            "test@example.com"
        )
        assert result is not None
        assert result.email == "test@example.com"
        assert result.id == "507f1f77bcf86cd799439011"

    async def test_get_user_by_email_not_found(self):
        db_manager.db.users.find_one = AsyncMock(return_value=None)

        result = await db_manager.get_auth_crud().get_user_by_email(
            "nonexistent@example.com"
        )
        assert result is None

    async def test_create_user(self):
        mock_insert_result = type(
            "obj", (object,), {"inserted_id": "507f1f77bcf86cd799439011"}
        )()

        db_manager.db.users.insert_one = AsyncMock(
            return_value=mock_insert_result
        )
        db_manager.db.users.find_one = AsyncMock(
            return_value={
                "_id": "507f1f77bcf86cd799439011",
                "email": "new@example.com",
                "password_hash": "hashed_password",
                "roles": ["user"],
                "is_banned": False,
                "created_at": "2024-01-01T00:00:00",
                "last_login_at": None,
            }
        )

        result = await db_manager.get_auth_crud().create_user(
            email="new@example.com",
            password_hash="hashed_password",
            roles=["user"],
        )

        assert result.email == "new@example.com"
        assert result.id == "507f1f77bcf86cd799439011"

    async def test_update_user_last_login(self):
        mock_update_result = type("obj", (object,), {"modified_count": 1})()
        db_manager.db.users.update_one = AsyncMock(
            return_value=mock_update_result
        )
        db_manager.db.users.find_one = AsyncMock(
            return_value={
                "_id": "507f1f77bcf86cd799439011",
                "email": "test@example.com",
                "password_hash": "hashed_password",
                "roles": ["user"],
                "is_banned": False,
                "created_at": "2024-01-01T00:00:00",
                "last_login_at": "2024-01-01T12:00:00",
            }
        )

        result = await db_manager.get_auth_crud().update_user_last_login(
            "test@example.com"
        )
        assert result is not None
        assert result.last_login_at == datetime.datetime(2024, 1, 1, 12, 0)

    async def test_get_refresh_token(self):
        mock_data = {
            "_id": "507f1f77bcf86cd799439012",
            "user_id": "507f1f77bcf86cd799439011",
            "token": "refresh_token_value",
            "expired_at": "2024-01-08T00:00:00",
            "used": False,
        }

        db_manager.db.tokens.find_one = AsyncMock(return_value=mock_data)

        result = await db_manager.get_token_crud().get_refresh_token(
            "refresh_token_value"
        )
        assert result is not None
        assert result["user_id"] == "507f1f77bcf86cd799439011"
        assert result["token"] == "refresh_token_value"

    async def test_mark_token_as_used(self):
        mock_update_result = type("obj", (object,), {"modified_count": 1})()
        db_manager.db.tokens.update_one = AsyncMock(
            return_value=mock_update_result
        )

        result = await db_manager.get_token_crud().mark_token_as_used(
            "refresh_token_value"
        )
        assert result is True
