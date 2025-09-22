from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    model_validator,
)

from auth_admin.models.user_role import UserRole
from settings import settings


class UserBase(BaseModel):
    email: EmailStr
    is_banned: bool = False
    roles: list[UserRole] = Field(default_factory=list)
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserDB(BaseModel):
    id: str
    email: EmailStr
    password_hash: str
    is_banned: bool = False
    roles: list[UserRole]
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_banned: bool = False
    roles: list[UserRole] = Field(default_factory=list)
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "is_banned": False,
                "roles": ["USER"],
                "created_at": "2023-10-01T12:00:00Z",
                "last_login_at": "2023-10-05T14:30:00Z",
            }
        }
    )


class CreateUserForm(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=settings.MIN_PASSWORD_LENGTH,
        max_length=settings.MAX_PASSWORD_LENGTH,
        description=f"Password must be between {settings.MIN_PASSWORD_LENGTH} and {settings.MAX_PASSWORD_LENGTH} characters",
    )
    roles: list[UserRole] = Field(
        default=[UserRole.USER], description="User roles"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "roles": ["USER"],
            }
        }
    )


class UserUpdateForm(BaseModel):
    is_banned: Optional[bool] = Field(None, description="Ban/unban user")
    roles: Optional[list[UserRole]] = Field(
        None, description="Update user roles"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"is_banned": False, "roles": ["USER", "ADMIN"]}
        }
    )


class LoginForm(BaseModel):
    email: str
    password: SecretStr
