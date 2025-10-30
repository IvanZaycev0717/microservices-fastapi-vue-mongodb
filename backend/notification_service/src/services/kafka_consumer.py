import asyncio
import json
import threading
from typing import Any

from confluent_kafka import Consumer, KafkaError, KafkaException

from logger import get_logger
from models.notification import NotificationCreate
from services.database import db_manager
from services.email_sending import send_notification_email
from settings import settings

logger = get_logger("KafkaConsumer")


class KafkaConsumer:
    """Kafka message consumer for notification service.

    Handles configuration, message consumption, and lifecycle management
    for Kafka consumer in a separate thread.

    Attributes:
        conf: Kafka consumer configuration dictionary.
        consumer: Confluent Kafka Consumer instance.
        running: Flag indicating if consumer is actively running.
        consumer_thread: Thread running the consumer loop.
        main_loop: Reference to the main asyncio event loop.
    """

    def __init__(self):
        self.conf = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "notification-service",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
        self.consumer: Consumer | None = None
        self.running = False
        self.consumer_thread: threading.Thread | None = None
        self.main_loop = None

    async def initialize(self):
        """Initializes Kafka consumer and subscribes to topics.

        Sets up the Kafka consumer with configuration and subscribes to
        password reset related topics.

        Raises:
            Exception: If consumer initialization or topic subscription fails.

        Note:
            - Subscribes to both password reset request and success topics
            - Logs successful subscription to configured topics
        """
        try:
            self.consumer = Consumer(self.conf)
            topics = [
                settings.KAFKA_PASSWORD_RESET_TOPIC,
                settings.KAFKA_PASSWORD_RESET_SUCCESS_TOPIC,
            ]
            self.consumer.subscribe(topics)
            logger.info(f"Subscribed to topics: {topics}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            raise

    async def consume_messages(self):
        """Starts the Kafka message consumption loop in a separate thread.

        Runs a blocking consumer that polls for messages and processes them
        in the main asyncio event loop using thread-safe coroutine execution.

        Note:
            - Runs consumer in daemon thread to allow graceful shutdown
            - Handles various Kafka errors with appropriate logging and retry logic
            - Commits offsets only after successful message processing
            - Uses thread-safe asyncio coroutine execution for message processing
        """
        self.running = True
        self.main_loop = asyncio.get_running_loop()

        def _run_consumer():
            """Blocking consumer running in separate thread"""
            logger.info("Starting Kafka consumer thread")

            while self.running:
                try:
                    msg = self.consumer.poll(1.0)

                    if msg is None:
                        continue

                    if msg.error():
                        error_code = msg.error().code()

                        if error_code == KafkaError._PARTITION_EOF:
                            continue
                        elif error_code == KafkaError.UNKNOWN_TOPIC_OR_PART:
                            logger.warning(
                                f"Topic not available: {msg.topic()}, retrying..."
                            )
                            continue
                        elif error_code == KafkaError._ALL_BROKERS_DOWN:
                            logger.error(
                                "All Kafka brokers are down, retrying..."
                            )
                            continue
                        elif error_code == KafkaError._TRANSPORT:
                            logger.error("Kafka transport error, retrying...")
                            continue
                        else:
                            logger.error(f"Kafka error: {msg.error()}")
                            continue

                    asyncio.run_coroutine_threadsafe(
                        self.process_message(msg), self.main_loop
                    )

                    self.consumer.commit(msg)

                except KafkaException as e:
                    logger.error(f"Kafka exception: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error in consumer thread: {e}")

        self.consumer_thread = threading.Thread(
            target=_run_consumer, daemon=True
        )
        self.consumer_thread.start()
        logger.info("Kafka consumer thread started")

    async def process_message(self, msg):
        """Process incoming Kafka message in main event loop.

        Decodes and routes Kafka messages to appropriate handlers based on topic.

        Args:
            msg: The Kafka message object to process.

        Note:
            - Handles JSON decoding errors for malformed messages
            - Routes messages to specific handlers based on topic
            - Logs message reception and processing errors
        """
        try:
            message_data = json.loads(msg.value().decode("utf-8"))
            logger.info(f"Received message from topic: {msg.topic()}")

            if msg.topic() == settings.KAFKA_PASSWORD_RESET_TOPIC:
                await self.handle_password_reset_request(message_data)
            elif msg.topic() == settings.KAFKA_PASSWORD_RESET_SUCCESS_TOPIC:
                await self.handle_password_reset_success(message_data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def handle_password_reset_request(
        self, message_data: dict[str, Any]
    ):
        """Handle password reset request message.

        Processes password reset request by creating notification record and
        triggering email sending task.

        Args:
            message_data: Dictionary containing reset request data with keys:
                - email: User email address
                - reset_token: Password reset token
                - user_id: User identifier

        Note:
            - Creates notification record in database before sending email
            - Spawns async task for email sending to avoid blocking
            - Handles missing fields in message data with KeyError
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

        Processes password reset success confirmation by creating notification
        record and triggering success email sending task.

        Args:
            message_data: Dictionary containing reset success data with keys:
                - email: User email address
                - user_id: User identifier

        Note:
            - Creates notification record in database before sending email
            - Spawns async task for email sending to avoid blocking
            - Handles missing fields in message data with KeyError
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
        """Stop the Kafka consumer.

        Gracefully stops the consumer thread and closes the Kafka consumer.

        Note:
            - Sets running flag to false to stop the consumption loop
            - Waits for consumer thread to finish with timeout
            - Closes Kafka consumer to release resources
            - Logs consumer shutdown completion
        """
        self.running = False
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5.0)
        if self.consumer:
            self.consumer.close()
        logger.info("Kafka consumer stopped")


kafka_consumer = KafkaConsumer()
