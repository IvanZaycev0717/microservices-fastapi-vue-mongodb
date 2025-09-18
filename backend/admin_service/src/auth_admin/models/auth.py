from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from auth_admin.crud.auth import UserRole
from settings import settings


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_banned: bool
    roles: list[UserRole]
    created_at: datetime
    last_login_at: datetime | None


class UserInDB(UserResponse):
    hashed_password: str


class CreateUserForm(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=settings.MIN_PASSWORD_LENGTH,
        max_length=settings.MAX_PASSWORD_LENGTH,
    )
    roles: list[UserRole] = Field(default=[UserRole.USER])


class UserUpdateForm(BaseModel):
    is_banned: bool | None = Field(None, description="Ban/unban user")
    roles: list[UserRole] | None = Field(None, description="Update user roles")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    email: EmailStr
    roles: list[str] = Field(default_factory=list)
    exp: datetime
    iat: datetime
