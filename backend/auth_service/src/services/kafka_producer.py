import json
import logging
from typing import Any

from confluent_kafka import Producer
from pydantic import BaseModel

from settings import settings

logger = logging.getLogger(f"{settings.GRPC_AUTH_NAME} - KafkaProducer")


class PasswordResetMessage(BaseModel):
    """Data model for password reset messages.

    Attributes:
        email: User's email address.
        reset_token: Generated password reset token.
        user_id: Unique user identifier.
    """

    email: str
    reset_token: str
    user_id: str


class KafkaProducer:
    """Kafka producer for sending messages to notification service.

    Attributes:
        conf: Kafka producer configuration dictionary.
        _producer: Confluent Kafka Producer instance.
        _initialized: Flag indicating if producer is initialized.
    """

    def __init__(self) -> None:
        """Initializes Kafka producer with configuration."""
        self.conf = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "acks": "all",
            "retries": 3,
            "client.id": "auth-service",
        }
        self._producer: Producer | None = None
        self._initialized: bool = False

    async def initialize(self) -> None:
        """Explicitly initialize Kafka producer.

        Should be called after Kafka cluster is confirmed to be ready.

        Raises:
            RuntimeError: If producer initialization fails.
        """
        if not self._initialized:
            try:
                self._producer = Producer(self.conf)
                self._initialized = True
                logger.info("Kafka producer initialized successfully")
            except Exception as e:
                logger.error(f"Kafka producer initialization failed: {e}")
                raise RuntimeError(
                    "Failed to initialize Kafka producer"
                ) from e

    @property
    def producer(self) -> Producer:
        """Get Kafka producer instance.

        Returns:
            Producer: Configured Kafka producer instance.

        Raises:
            RuntimeError: If producer is not initialized.
        """
        if not self._initialized or self._producer is None:
            raise RuntimeError(
                "Kafka producer not initialized. Call initialize() first."
            )
        return self._producer

    def _delivery_report(self, err: Any, msg: Any) -> None:
        """Callback for message delivery reports.

        Args:
            err: Error object if delivery failed.
            msg: Message object if delivery succeeded.

        Logs:
            Error message if delivery failed, debug info if successful.
        """
        if err:
            logger.warning(f"Message delivery failed (will retry): {err}")
        else:
            logger.debug(
                f"Message delivered to {msg.topic()} [{msg.partition()}]"
            )

    def send_password_reset(self, message: PasswordResetMessage) -> bool:
        """Send password reset message to Kafka topic.

        Args:
            message: PasswordResetMessage instance with reset data.

        Returns:
            bool: True if message was queued successfully, False otherwise.

        Raises:
            BufferError: If producer message queue is full.
            Exception: For any other unexpected errors during message production.
        """
        try:
            message_dict = message.model_dump()
            value = json.dumps(message_dict).encode("utf-8")

            self.producer.produce(
                topic=settings.KAFKA_PASSWORD_RESET_TOPIC,
                value=value,
                callback=self._delivery_report,
            )

            self.producer.poll(1)
            logger.info(f"Password reset message sent for: {message.email}")
            return True

        except BufferError as e:
            logger.error(f"Producer queue full: {e}")
            return False
        except Exception as e:
            logger.exception(f"Failed to send password reset message: {e}")
            return False

    def flush(self) -> None:
        """Wait for all outstanding messages to be delivered.

        Blocks until all messages in the producer queue are delivered
        or timeout occurs.
        """
        if self._producer:
            self._producer.flush()
            logger.info("Kafka producer flushed")

    def close(self) -> None:
        """Close the producer connection.

        Flushes any outstanding messages and closes the producer connection.
        """
        if self._producer:
            self.flush()
            self._producer = None
            self._initialized = False
            logger.info("Kafka producer closed")


# Global instance
kafka_producer = KafkaProducer()
