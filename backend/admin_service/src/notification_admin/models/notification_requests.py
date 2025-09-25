from typing import Any

from pydantic import BaseModel, Field, field_validator

from notification_admin.models.notification_base import (
    NotificationChannel,
    NotificationChannelRequest,
)


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


class BulkNotificationCreateRequest(BaseModel):
    notifications: list[NotificationCreateRequest] = Field(min_length=1)
    batch_id: str | None = Field(
        None, description="ID для группировки уведомлений"
    )


class TemplateNotificationRequest(BaseModel):
    template_name: str = Field(min_length=1, max_length=100)
    user_id: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    channels: list[NotificationChannel] = Field(min_length=1)
