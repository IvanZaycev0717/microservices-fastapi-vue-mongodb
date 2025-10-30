from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

from settings import settings


class UserBase(BaseModel):
    email: EmailStr
    is_banned: bool = False
    roles: list[str] = Field(default_factory=list)
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserDB(BaseModel):
    id: str
    email: EmailStr
    password_hash: str
    is_banned: bool = False
    roles: list[str]
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_banned: bool = False
    roles: list[str] = Field(default_factory=list)
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "is_banned": False,
                "roles": ["user"],
                "created_at": "2023-10-01T12:00:00Z",
                "last_login_at": "2023-10-05T14:30:00Z",
            }
        }
    )


class CreateUserRequest(BaseModel):
    email: EmailStr = Field(
        min_length=settings.MIN_EMAIL_LENGTH,
        max_length=settings.MAX_EMAIL_LENGTH,
    )
    password: SecretStr = Field(
        min_length=settings.MIN_PASSWORD_LENGTH,
        max_length=settings.MAX_PASSWORD_LENGTH,
        description=f"Password must be between {settings.MIN_PASSWORD_LENGTH} and {settings.MAX_PASSWORD_LENGTH} characters",
    )
    roles: list[str] = Field(default=["user"], description="User roles")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "roles": ["user"],
            }
        }
    )


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        min_length=settings.MIN_EMAIL_LENGTH,
        max_length=settings.MAX_EMAIL_LENGTH,
    )
    password: SecretStr = Field(
        min_length=settings.MIN_PASSWORD_LENGTH,
        max_length=settings.MAX_PASSWORD_LENGTH,
        description=f"Password must be between {settings.MIN_PASSWORD_LENGTH} and {settings.MAX_PASSWORD_LENGTH} characters",
    )


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    expires_in: int


class TokenPayload(BaseModel):
    sub: str
    email: EmailStr
    roles: list[str] = Field(default_factory=list)
    user_id: Optional[str] = None
    type: Optional[str] = None
    exp: int
    iat: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(
        min_length=settings.MIN_EMAIL_LENGTH,
        max_length=settings.MAX_EMAIL_LENGTH,
    )


class ForgotPasswordResponse(BaseModel):
    success: bool
    reset_token: str
    message: str


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: SecretStr = Field(
        min_length=settings.MIN_PASSWORD_LENGTH,
        max_length=settings.MAX_PASSWORD_LENGTH,
        description=f"Password must be between {settings.MIN_PASSWORD_LENGTH} and {settings.MAX_PASSWORD_LENGTH} characters",
    )
    email: EmailStr = Field(
        min_length=settings.MIN_EMAIL_LENGTH,
        max_length=settings.MAX_EMAIL_LENGTH,
    )


class ResetPasswordResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    email: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Password successfully reset",
                "user_id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
            }
        }
    )
