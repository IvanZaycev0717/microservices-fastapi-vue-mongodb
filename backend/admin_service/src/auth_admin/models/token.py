from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional

from auth_admin.models.user_role import UserRole


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    expires_in: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "507f1f77bcf86cd799439011",
                "expires_in": 3600
            }
        }
    )


class TokenPayload(BaseModel):
    sub: str
    email: EmailStr
    roles: list[UserRole] = Field(default_factory=list)
    user_id: Optional[str] = None
    type: Optional[str] = None
    exp: int
    iat: int

    @field_validator("exp", "iat", mode="before")
    @classmethod
    def convert_datetime_to_timestamp(cls, v):
        if isinstance(v, datetime):
            return int(v.timestamp())
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sub": "user@example.com",
                "email": "user@example.com",
                "roles": ["USER"],
                "user_id": "507f1f77bcf86cd799439011",
                "type": "access",
                "exp": 1696500000,
                "iat": 1696413600
            }
        }
    )
