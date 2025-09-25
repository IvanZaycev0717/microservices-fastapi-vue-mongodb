from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class NotificationCreate(BaseModel):
    to_email: EmailStr  # получатель письма
    subject: str = Field(min_length=1, max_length=200)  # тема письма
    message: str = Field(min_length=1)  # сообщение письма


class NotificationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    to_email: EmailStr
    subject: str
    message: str
    status: str
    created_at: datetime
    sent_at: datetime | None = None

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        return str(v)


class BanNotification(BaseModel):
    email: EmailStr
    subject: str
    message: str
