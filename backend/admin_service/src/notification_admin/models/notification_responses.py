from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from notification_admin.models.notification_base import (
    NotificationChannel,
    NotificationStatus,
)


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


class BulkNotificationResponse(BaseModel):
    batch_id: str
    created_count: int
    notifications: list[NotificationResponse]
    errors: list[dict[str, Any]] = Field(default_factory=list)
