from datetime import datetime
from typing import Any

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from notification_admin.models.notification_base import (
    NotificationCreateRequest,
    NotificationInDB,
    NotificationStatus,
)
from services.logger import get_logger

logger = get_logger(__name__)


class NotificationCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.notifications

    # CREATE
    async def create(
        self, notification_data: NotificationCreateRequest | dict[str, Any]
    ) -> str:
        """
        Создает новое уведомление в базе данных

        Args:
            notification_data: Данные уведомления (модель Pydantic или dict)

        Returns:
            ID созданного уведомления

        Raises:
            ValueError: Если данные некорректны
            Exception: При ошибках базы данных
        """
        try:
            # Конвертируем Pydantic модель в dict если необходимо
            if isinstance(notification_data, NotificationCreateRequest):
                data_dict = notification_data.model_dump()
            else:
                data_dict = notification_data

            # Создаем модель для базы данных
            notification_db = NotificationInDB(
                event_type=data_dict["event_type"],
                user_id=data_dict.get("user_id"),
                channels=self._prepare_channels_data(data_dict["channels"]),
                priority=data_dict.get("priority", 1),
                metadata=data_dict.get("metadata"),
                status=NotificationStatus.PENDING,
            )

            # Конвертируем в dict для MongoDB
            notification_dict = notification_db.model_dump(
                by_alias=True, exclude_none=True
            )

            # Вставляем документ в базу
            result = await self.collection.insert_one(notification_dict)

            logger.info(
                f"Notification created successfully. ID: {result.inserted_id}, "
                f"Event: {data_dict['event_type']}, User: {data_dict.get('user_id', 'N/A')}"
            )

            return str(result.inserted_id)

        except ValueError as e:
            logger.error(f"Validation error creating notification: {e}")
            raise ValueError(f"Invalid notification data: {e}")
        except Exception as e:
            logger.error(f"Database error creating notification: {e}")
            raise Exception(f"Failed to create notification: {e}")

    async def create_bulk(
        self,
        notifications_data: list[NotificationCreateRequest | dict[str, Any]],
    ) -> list[str]:
        """
        Массовое создание уведомлений

        Args:
            notifications_data: Список данных уведомлений

        Returns:
            Список ID созданных уведомлений
        """
        try:
            documents = []
            for notification_data in notifications_data:
                if isinstance(notification_data, NotificationCreateRequest):
                    data_dict = notification_data.model_dump()
                else:
                    data_dict = notification_data

                notification_db = NotificationInDB(
                    event_type=data_dict["event_type"],
                    user_id=data_dict.get("user_id"),
                    channels=self._prepare_channels_data(
                        data_dict["channels"]
                    ),
                    priority=data_dict.get("priority", 1),
                    metadata=data_dict.get("metadata"),
                    status=NotificationStatus.PENDING,
                )

                documents.append(
                    notification_db.model_dump(
                        by_alias=True, exclude_none=True
                    )
                )

            if not documents:
                return []

            result = await self.collection.insert_many(documents)

            logger.info(
                f"Bulk creation: {len(result.inserted_ids)} notifications created"
            )

            return [str(id) for id in result.inserted_ids]

        except Exception as e:
            logger.error(f"Database error in bulk notification creation: {e}")
            raise Exception(f"Failed to create bulk notifications: {e}")

    def _prepare_channels_data(
        self, channels_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Подготавливает данные каналов для сохранения в БД

        Args:
            channels_data: Данные каналов из запроса

        Returns:
            Подготовленные данные каналов
        """
        prepared_channels = []

        for channel_data in channels_data:
            channel_dict = {
                "channel": channel_data["channel"],
                "recipient": channel_data["recipient"],
                "content": channel_data["content"],
                "scheduled_at": channel_data.get("scheduled_at"),
                "status": NotificationStatus.PENDING.value,
                "attempts": 0,
                "created_at": datetime.now(),
            }
            prepared_channels.append(channel_dict)

        return prepared_channels

    async def create_with_template(
        self,
        template_data: dict[str, Any],
        user_id: str,
        parameters: dict[str, Any],
    ) -> str:
        """
        Создает уведомление на основе шаблона

        Args:
            template_data: Данные шаблона
            user_id: ID пользователя
            parameters: Параметры для подстановки в шаблон

        Returns:
            ID созданного уведомления
        """
        try:
            # Здесь может быть логика рендеринга шаблона
            rendered_channels = self._render_template_channels(
                template_data, user_id, parameters
            )

            notification_data = {
                "event_type": template_data.get(
                    "event_type", "template_notification"
                ),
                "user_id": user_id,
                "channels": rendered_channels,
                "priority": template_data.get("priority", 1),
                "metadata": {
                    "template_name": template_data.get("name"),
                    "template_parameters": parameters,
                    "is_template_based": True,
                },
            }

            return await self.create(notification_data)

        except Exception as e:
            logger.error(f"Error creating notification from template: {e}")
            raise Exception(
                f"Failed to create notification from template: {e}"
            )

    def _render_template_channels(
        self,
        template_data: dict[str, Any],
        user_id: str,
        parameters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Рендерит каналы уведомления из шаблона

        Args:
            template_data: Данные шаблона
            user_id: ID пользователя
            parameters: Параметры для подстановки

        Returns:
            Список подготовленных каналов
        """
        # Базовая реализация - в реальном проекте здесь будет сложная логика рендеринга
        channels = []

        for channel_template in template_data.get("channels", []):
            channel_type = channel_template["channel"]
            content_template = channel_template["content"]

            # Простая подстановка параметров (заменить на реальный шаблонизатор)
            rendered_content = self._render_content(
                content_template, parameters
            )

            channel_data = {
                "channel": channel_type,
                "recipient": channel_template.get("recipient", "").format(
                    user_id=user_id, **parameters
                ),
                "content": rendered_content,
                "scheduled_at": channel_template.get("scheduled_at"),
            }

            channels.append(channel_data)

        return channels

    def _render_content(
        self, content_template: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Рендерит содержимое уведомления

        Args:
            content_template: Шаблон содержимого
            parameters: Параметры для подстановки

        Returns:
            Рендеренное содержимое
        """
        # Простая реализация - заменить на реальный шаблонизатор
        rendered = {}
        for key, value in content_template.items():
            if isinstance(value, str):
                rendered[key] = value.format(**parameters)
            else:
                rendered[key] = value
        return rendered
