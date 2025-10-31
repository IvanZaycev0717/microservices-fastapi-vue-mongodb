import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from aiokafka import AIOKafkaProducer

from settings import settings

logger = logging.getLogger("BaseKafkaProducer")


class BaseKafkaProducer(ABC):
    """Base async Kafka producer using aiokafka.

    Attributes:
        producer: AIOKafkaProducer instance.
        _initialized: Flag indicating if producer is initialized.
    """

    def __init__(self):
        self.producer: AIOKafkaProducer | None = None
        self._initialized: bool = False

    async def connect(self):
        """Initialize async Kafka producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=self._get_client_id(),
            )
            await self.producer.start()
            self._initialized = True
            logger.info(f"{self._get_client_id()} connected successfully")
        except Exception as e:
            logger.exception(f"Failed to connect {self._get_client_id()}: {e}")
            raise

    async def send_message(self, topic: str, data: dict[str, Any]) -> bool:
        """Send message to Kafka topic asynchronously.

        Args:
            topic: Kafka topic name.
            data: dictionary with message data.

        Returns:
            bool: True if message was sent successfully, False otherwise.
        """
        if not self._initialized:
            logger.warning(f"{self._get_client_id()} not initialized")
            return False

        try:
            value = json.dumps(data).encode("utf-8")
            await self.producer.send_and_wait(topic=topic, value=value)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False

    async def close(self):
        """Close producer connection asynchronously."""
        if self.producer:
            await self.producer.stop()
            self._initialized = False
            logger.info(f"{self._get_client_id()} closed")

    @abstractmethod
    def _get_client_id(self) -> str:
        """Get client ID for Kafka configuration."""
        pass
