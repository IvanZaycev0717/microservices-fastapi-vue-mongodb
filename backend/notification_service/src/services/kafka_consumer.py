import asyncio
import json
from typing import Any

from aiokafka import AIOKafkaConsumer

from logger import get_logger
from models.notification import NotificationCreate
from services.database import db_manager
from services.email_sending import send_notification_email
from settings import settings

logger = get_logger("KafkaConsumer")


class KafkaConsumer:
    """Kafka message consumer for notification service using aiokafka.

    Handles async message consumption for notification topics with pure asyncio.

    Attributes:
        consumer: AIOKafkaConsumer instance for message consumption.
        running: Flag indicating if consumer is actively running.
        _consume_task: Asyncio task for message consumption loop.
    """

    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self.running = False
        self._consume_task: asyncio.Task | None = None

    async def initialize(self):
        """Initializes Kafka consumer and subscribes to topics.

        Sets up the AIOKafkaConsumer with configuration for notification topics.

        Raises:
            Exception: If consumer initialization fails.
        """
        try:
            self.consumer = AIOKafkaConsumer(
                settings.KAFKA_PASSWORD_RESET_TOPIC,
                settings.KAFKA_PASSWORD_RESET_SUCCESS_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id="notification-service",
                auto_offset_reset="earliest",
                enable_auto_commit=False,
            )

            await self.consumer.start()
            logger.info("Kafka consumer initialized with aiokafka")

        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            raise

    async def consume_messages(self):
        """Starts the Kafka message consumption loop.

        Begins async message consumption using AIOKafkaConsumer's async iterator.
        """
        self.running = True
        self._consume_task = asyncio.create_task(self._consume_loop())
        logger.info("Kafka message consumption started")

    async def _consume_loop(self):
        """Main message consumption loop using async iterator."""
        try:
            async for msg in self.consumer:
                if not self.running:
                    break
                await self.process_message(msg)
        except Exception as e:
            logger.exception(f"Error in consumption loop: {e}")
        finally:
            await self.consumer.stop()

    async def process_message(self, msg):
        """Process incoming Kafka message.

        Args:
            msg: The Kafka message object to process.

        Note:
            - Handles JSON decoding errors for malformed messages
            - Routes messages to specific handlers based on topic
        """
        try:
            message_data = json.loads(msg.value.decode("utf-8"))
            logger.info(f"Received message from topic: {msg.topic}")

            if msg.topic == settings.KAFKA_PASSWORD_RESET_TOPIC:
                await self.handle_password_reset_request(message_data)
            elif msg.topic == settings.KAFKA_PASSWORD_RESET_SUCCESS_TOPIC:
                await self.handle_password_reset_success(message_data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def handle_password_reset_request(
        self, message_data: dict[str, Any]
    ):
        """Handle password reset request message.

        Args:
            message_data: Dictionary containing reset request data.
        """
        try:
            notification = NotificationCreate(
                email=message_data["email"],
                reset_token=message_data["reset_token"],
                user_id=message_data["user_id"],
                message_type="reset_request",
            )

            crud = db_manager.get_notification_crud()
            notification_id = await crud.create(
                notification,
                subject="Сброс пароля",
                message=f"Токен для сброса пароля: {message_data['reset_token']}",
            )

            asyncio.create_task(
                send_notification_email(
                    notification_id,
                    message_data["email"],
                    "reset_request",
                    reset_token=message_data["reset_token"],
                )
            )

            logger.info(
                f"Password reset notification created for: {message_data['email']}"
            )

        except KeyError as e:
            logger.error(f"Missing field in reset request message: {e}")
        except Exception as e:
            logger.error(f"Error handling reset request: {e}")

    async def handle_password_reset_success(
        self, message_data: dict[str, Any]
    ):
        """Handle password reset success message.

        Args:
            message_data: Dictionary containing reset success data.
        """
        try:
            notification = NotificationCreate(
                email=message_data["email"],
                user_id=message_data["user_id"],
                message_type="reset_success",
            )

            crud = db_manager.get_notification_crud()
            notification_id = await crud.create(
                notification,
                subject="Пароль успешно изменен",
                message="Ваш пароль был успешно изменен",
            )

            asyncio.create_task(
                send_notification_email(
                    notification_id, message_data["email"], "reset_success"
                )
            )

            logger.info(
                f"Password reset success notification created for: {message_data['email']}"
            )

        except KeyError as e:
            logger.error(f"Missing field in reset success message: {e}")
        except Exception as e:
            logger.error(f"Error handling reset success: {e}")

    async def stop(self):
        """Stop the Kafka consumer gracefully."""
        self.running = False
        if self._consume_task:
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                pass
        logger.info("Kafka consumer stopped")


kafka_consumer = KafkaConsumer()
