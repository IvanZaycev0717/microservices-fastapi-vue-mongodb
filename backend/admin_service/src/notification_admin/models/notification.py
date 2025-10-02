import html
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from settings import settings


class NotificationCreate(BaseModel):
    """Request model for creating notifications.

    Attributes:
        to_email (EmailStr): Recipient email address.
        subject (str): Email subject within length boundaries.
        message (str): Email message within length boundaries.

    Note:
        Automatically escapes HTML in subject and message fields.
    """

    to_email: EmailStr  # получатель письма
    subject: str = Field(
        min_length=settings.MIN_EMAIL_SUBJECT_LENGHT,
        max_length=settings.MAX_EMAIL_SUBJECT_LENGHT,
    )  # тема письма
    message: str = Field(
        min_length=settings.MIN_EMAIL_MESSAGE_LENGTH,
        max_length=settings.MAX_EMAIL_MESSAGE_LENGHT,
    )  # сообщение письма

    @field_validator("subject", "message")
    @classmethod
    def escape_html(cls, v: str) -> str:
        return html.escape(v)


class NotificationResponse(BaseModel):
    """Response model for notification data.

    Attributes:
        id (str): Notification identifier.
        to_email (EmailStr): Recipient email address.
        subject (str): Email subject.
        message (str): Email message content.
        status (str): Current notification status.
        created_at (datetime): Creation timestamp.
        sent_at (datetime | None): Sent timestamp if applicable.
    """

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
    """Model for ban notification data.

    Attributes:
        email (EmailStr): Banned user's email address.
        subject (str): Notification subject.
        message (str): Notification message content.
    """

    email: EmailStr
    subject: str
    message: str
