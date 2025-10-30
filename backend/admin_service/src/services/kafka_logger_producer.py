import json
import logging

from confluent_kafka.experimental.aio import AIOProducer

from settings import settings

logger = logging.getLogger("KafkaLoggerProducer")


class KafkaLoggerProducer:
    """Kafka producer for sending logs to Kafka topic."""

    def __init__(self):
        self.producer: AIOProducer | None = None
        self.config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "enable.idempotence": True,
            "acks": "all",
            "retries": 3,
        }

    async def connect(self):
        """Initialize async Kafka producer for logs."""
        try:
            self.producer = AIOProducer(self.config)
            logger.info("Kafka logger producer connected successfully")
        except Exception:
            logger.exception("Failed to connect Kafka logger producer")
            raise

    async def send_log(self, log_data: dict):
        """Send log entry to Kafka topic.

        Args:
            log_data: Dictionary with log data
        """
        if not self.producer or not settings.KAFKA_LOGS_ENABLED:
            return False

        try:
            value = json.dumps(log_data).encode("utf-8")
            future = await self.producer.produce(
                topic=settings.KAFKA_LOGS_TOPIC,
                value=value,
            )
            await future
            return True
        except Exception:
            return False

    async def close(self):
        """Close producer connection."""
        if self.producer:
            await self.producer.flush()
            await self.producer.close()


kafka_logger_producer = KafkaLoggerProducer()
