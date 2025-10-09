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

logger = get_logger(f"{settings.NOTIFICATION_SERVICE_NAME} - KafkaConsumer")


class KafkaConsumer:
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
        """Initialize Kafka consumer"""
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
        """Start Kafka consumer in separate thread"""
        self.running = True
        self.main_loop = asyncio.get_running_loop()  # Сохраняем основной event loop
        
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
                            logger.warning(f"Topic not available: {msg.topic()}, retrying...")
                            continue
                        elif error_code == KafkaError._ALL_BROKERS_DOWN:
                            logger.error("All Kafka brokers are down, retrying...")
                            continue
                        elif error_code == KafkaError._TRANSPORT:
                            logger.error("Kafka transport error, retrying...")
                            continue
                        else:
                            logger.error(f"Kafka error: {msg.error()}")
                            continue

                    # Используем сохраненный main_loop для запуска корутины
                    asyncio.run_coroutine_threadsafe(
                        self.process_message(msg), 
                        self.main_loop
                    )
                    
                    self.consumer.commit(msg)

                except KafkaException as e:
                    logger.error(f"Kafka exception: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error in consumer thread: {e}")

        # Start consumer in separate thread
        self.consumer_thread = threading.Thread(target=_run_consumer, daemon=True)
        self.consumer_thread.start()
        logger.info("Kafka consumer thread started")

    async def process_message(self, msg):
        """Process incoming Kafka message in main event loop"""
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

    async def handle_password_reset_request(self, message_data: dict[str, Any]):
        """Handle password reset request message"""
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

            logger.info(f"Password reset notification created for: {message_data['email']}")

        except KeyError as e:
            logger.error(f"Missing field in reset request message: {e}")
        except Exception as e:
            logger.error(f"Error handling reset request: {e}")

    async def handle_password_reset_success(self, message_data: dict[str, Any]):
        """Handle password reset success message"""
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

            logger.info(f"Password reset success notification created for: {message_data['email']}")

        except KeyError as e:
            logger.error(f"Missing field in reset success message: {e}")
        except Exception as e:
            logger.error(f"Error handling reset success: {e}")

    async def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5.0)
        if self.consumer:
            self.consumer.close()
        logger.info("Kafka consumer stopped")


kafka_consumer = KafkaConsumer()