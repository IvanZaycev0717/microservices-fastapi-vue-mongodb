import logging
from typing import Any

from services.base_kafka_producer import BaseKafkaProducer
from settings import settings

logger = logging.getLogger("KafkaLoggerProducer")


class KafkaLoggerProducer(BaseKafkaProducer):
    """Kafka producer for sending logs to Kafka topic using aiokafka."""

    def _get_client_id(self) -> str:
        return "admin-service-logger"

    async def send_log(self, log_data: dict[str, Any]) -> bool:
        """Send log entry to Kafka topic.

        Args:
            log_data: dictionary with log data.

        Returns:
            bool: True if log was sent successfully, False otherwise.
        """
        if not settings.KAFKA_LOGS_ENABLED:
            return False

        return await self.send_message(settings.KAFKA_LOGS_TOPIC, log_data)


kafka_logger_producer = KafkaLoggerProducer()
