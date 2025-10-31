import asyncio
import logging
from typing import Optional

from services.base_kafka_producer import BaseKafkaProducer
from settings import settings

logger = logging.getLogger("KafkaProducer")


class KafkaCacheInvalidationProducer(BaseKafkaProducer):
    """Kafka producer for cache invalidation events using aiokafka."""

    def _get_client_id(self) -> str:
        return "admin-service-cache-invalidation"

    async def send_cache_invalidation(
        self, entity_type: str, action: str, entity_id: Optional[str] = None
    ) -> bool:
        """Send cache invalidation event to Kafka.

        Args:
            entity_type: Type of entity (about, projects, tech, etc.)
            action: Action performed (create, update, delete)
            entity_id: Optional entity identifier for targeted invalidation

        Returns:
            bool: True if message was sent successfully, False otherwise.
        """
        message = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": asyncio.get_event_loop().time(),
        }

        success = await self.send_message(
            settings.KAFKA_CACHE_INVALIDATION_TOPIC, message
        )

        if success:
            logger.info(f"Cache invalidation sent: {entity_type}.{action}")
        else:
            logger.error(
                f"Failed to send cache invalidation: {entity_type}.{action}"
            )

        return success


kafka_producer = KafkaCacheInvalidationProducer()
