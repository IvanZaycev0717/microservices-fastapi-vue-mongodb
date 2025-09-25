from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class NotificationType(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class EmailContent(BaseModel):
    subject: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    html_body: str | None = None
    cc: list[EmailStr] | None = None
    bcc: list[EmailStr] | None = None


class SMSContent(BaseModel):
    message: str = Field(min_length=1, max_length=1600)


class PushContent(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    image_url: str | None = None
    deep_link: str | None = None
    data: dict[str, Any] | None = None


class NotificationChannelRequest(BaseModel):
    channel: NotificationChannel
    recipient: str = Field(description="Email, phone number, or user ID")
    content: EmailContent | SMSContent | PushContent
    scheduled_at: datetime | None = None

    @field_validator("recipient")
    @classmethod
    def validate_recipient(cls, v: str, info: Any) -> str:
        channel = info.data.get("channel")
        if channel == NotificationChannel.EMAIL:
            if "@" not in v or "." not in v:
                raise ValueError("Invalid email format")
        elif channel == NotificationChannel.SMS:
            if not v.replace("+", "").replace(" ", "").isdigit():
                raise ValueError("Invalid phone number format")
        return v

    @field_validator("content")
    @classmethod
    def validate_content_type(cls, v: Any, info: Any) -> Any:
        channel = info.data.get("channel")
        if channel == NotificationChannel.EMAIL and not isinstance(
            v, EmailContent
        ):
            raise ValueError("Email channel requires EmailContent")
        elif channel == NotificationChannel.SMS and not isinstance(
            v, SMSContent
        ):
            raise ValueError("SMS channel requires SMSContent")
        elif channel == NotificationChannel.PUSH and not isinstance(
            v, PushContent
        ):
            raise ValueError("Push channel requires PushContent")
        return v


class NotificationCreateRequest(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    user_id: str | None = Field(None, description="ID пользователя в системе")
    channels: list[NotificationChannelRequest] = Field(min_length=1)
    priority: int = Field(default=1, ge=1, le=5)
    metadata: dict[str, Any] | None = None

    @field_validator("channels")
    @classmethod
    def validate_unique_channels(
        cls, v: list[NotificationChannelRequest]
    ) -> list[NotificationChannelRequest]:
        channels = [item.channel for item in v]
        if len(channels) != len(set(channels)):
            raise ValueError("Duplicate channels are not allowed")
        return v


class NotificationInDB(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat()},
        arbitrary_types_allowed=True,
    )

    id: str | None = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    user_id: str | None = None
    channels: list[dict[str, Any]]
    status: NotificationStatus = NotificationStatus.PENDING
    priority: int = 1
    metadata: dict[str, Any] | None = None


class NotificationUpdate(BaseModel):
    status: NotificationStatus | None = None
    error_message: str | None = None
    provider_message_id: str | None = None
    sent_at: datetime | None = None


class ChannelResponse(BaseModel):
    channel: NotificationChannel
    status: NotificationStatus
    recipient: str
    sent_at: datetime | None = None
    error_message: str | None = None
    provider_message_id: str | None = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    created_at: datetime
    event_type: str
    user_id: str | None = None
    channels: list[ChannelResponse]
    status: NotificationStatus
    metadata: dict[str, Any] | None = None


class BulkNotificationCreateRequest(BaseModel):
    notifications: list[NotificationCreateRequest] = Field(min_length=1)
    batch_id: str | None = Field(
        None, description="ID для группировки уведомлений"
    )


class BulkNotificationResponse(BaseModel):
    batch_id: str
    created_count: int
    notifications: list[NotificationResponse]
    errors: list[dict[str, Any]] = Field(default_factory=list)


class NotificationFilter(BaseModel):
    user_id: str | None = None
    status: NotificationStatus | None = None
    event_type: str | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None


class NotificationStats(BaseModel):
    total: int
    pending: int
    sent: int
    delivered: int
    failed: int
