import asyncio
import json

from confluent_kafka.experimental.aio import AIOProducer

from services.logger import get_logger
from settings import settings

logger = get_logger("KafkaProducer")


class KafkaCacheInvalidationProducer:
    """Kafka producer for cache invalidation events.

    Uses async producer to avoid blocking FastAPI main thread.
    """

    def __init__(self):
        self.producer: AIOProducer | None = None
        self.config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "enable.idempotence": settings.KAFKA_IS_IDEMPOTENCE_ENABLED,
            "acks": settings.KAFKA_ACKS,
            "retries": settings.KAFKA_RETRIES,
        }

    async def connect(self):
        """Initialize async Kafka producer."""
        try:
            self.producer = AIOProducer(self.config)
            logger.info("Kafka producer connected successfully")
        except Exception:
            logger.exception("Failed to connect Kafka producer")
            raise

    async def send_cache_invalidation(
        self, entity_type: str, action: str, entity_id: str | None = None
    ):
        """Send cache invalidation event to Kafka.

        Args:
            entity_type: Type of entity (about, projects, tech, etc.)
            action: Action performed (create, update, delete)
            entity_id: Optional entity identifier for targeted invalidation
        """
        if not self.producer:
            logger.warning("Kafka producer not connected")
            return False

        try:
            message = {
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "timestamp": asyncio.get_event_loop().time(),
            }

            value = json.dumps(message).encode("utf-8")

            future = await self.producer.produce(
                topic=settings.KAFKA_CACHE_INVALIDATION_TOPIC,
                value=value,
                key=entity_type.encode("utf-8"),
            )

            await future
            logger.debug(f"Cache invalidation sent: {entity_type}.{action}")
            return True

        except Exception:
            logger.exception(
                f"Failed to send cache invalidation for {entity_type}"
            )
            return False

    async def flush(self):
        """Flush any pending messages."""
        if self.producer:
            await self.producer.flush()

    async def close(self):
        """Close producer connection."""
        if self.producer:
            await self.flush()
            await self.producer.close()
            logger.info("Kafka producer closed")


kafka_producer = KafkaCacheInvalidationProducer()
