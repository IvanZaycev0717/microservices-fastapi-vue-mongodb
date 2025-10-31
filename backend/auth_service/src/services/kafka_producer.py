import asyncio
import json

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from logger import get_logger
from settings import settings

logger = get_logger("KafkaProducer")


class PasswordResetMessage(BaseModel):
    """Data model for password reset messages."""

    email: str
    reset_token: str
    user_id: str


class PasswordResetSuccessMessage(BaseModel):
    """Data model for password reset success messages."""

    email: str
    user_id: str


class KafkaProducer:
    """Async Kafka producer for sending messages using aiokafka.

    Attributes:
        producer: AIOKafkaProducer instance for async message production.
        _initialized: Flag indicating if producer is initialized.
    """

    def __init__(self) -> None:
        self.producer: AIOKafkaProducer | None = None
        self._initialized: bool = False

    async def initialize(
        self, max_retries: int = 5, retry_delay: int = 2
    ) -> None:
        """Initialize AIOKafkaProducer with retry mechanism.

        Args:
            max_retries: Maximum number of initialization attempts.
            retry_delay: Delay between retries in seconds.

        Raises:
            RuntimeError: If producer initialization fails after all retries.
        """
        for attempt in range(max_retries):
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    client_id="auth-service",
                )
                await self.producer.start()
                self._initialized = True
                logger.info(
                    "Kafka producer initialized successfully with aiokafka"
                )
                return

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Kafka producer initialization failed (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(
                        f"Kafka producer initialization failed after {max_retries} attempts: {e}"
                    )
                    raise RuntimeError(
                        "Failed to initialize Kafka producer"
                    ) from e

    async def send_password_reset(self, message: PasswordResetMessage) -> bool:
        """Send password reset message to Kafka topic asynchronously.

        Args:
            message: PasswordResetMessage instance with reset data.

        Returns:
            bool: True if message was sent successfully, False otherwise.
        """
        try:
            message_dict = message.model_dump()
            value = json.dumps(message_dict).encode("utf-8")

            await self.producer.send_and_wait(
                topic=settings.KAFKA_PASSWORD_RESET_TOPIC,
                value=value,
            )

            logger.info(f"Password reset message sent for: {message.email}")
            return True

        except Exception as e:
            logger.exception(f"Failed to send password reset message: {e}")
            return False

    async def send_password_reset_success(
        self, message: PasswordResetSuccessMessage
    ) -> bool:
        """Send password reset success message to Kafka topic asynchronously.

        Args:
            message: PasswordResetSuccessMessage instance with success data.

        Returns:
            bool: True if message was sent successfully, False otherwise.
        """
        try:
            message_dict = message.model_dump()
            value = json.dumps(message_dict).encode("utf-8")

            await self.producer.send_and_wait(
                topic=settings.KAFKA_PASSWORD_RESET_SUCCESS_TOPIC,
                value=value,
            )

            logger.info(
                f"Password reset success message sent for: {message.email}"
            )
            return True

        except Exception as e:
            logger.exception(
                f"Failed to send password reset success message: {e}"
            )
            return False

    async def close(self) -> None:
        """Close the producer connection asynchronously."""
        if self.producer:
            await self.producer.stop()
            self._initialized = False
            logger.info("Kafka producer closed")


kafka_producer = KafkaProducer()
