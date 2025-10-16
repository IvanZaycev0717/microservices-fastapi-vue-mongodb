from confluent_kafka.admin import AdminClient, NewTopic

from services.logger import get_logger
from settings import settings

logger = get_logger("KafkaTopicManager")


class KafkaTopicManager:
    """Manager for Kafka topic creation and validation."""

    def __init__(self):
        self.admin_client = AdminClient(
            {"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS}
        )

    async def ensure_topic_exists(
        self, topic_name: str, partitions: int = 1, replication_factor: int = 1
    ) -> bool:
        """Ensure Kafka topic exists, create if it doesn't.

        Args:
            topic_name: Name of the topic to ensure.
            partitions: Number of partitions for the topic.
            replication_factor: Replication factor for the topic.

        Returns:
            bool: True if topic exists or was created successfully.
        """
        try:
            metadata = self.admin_client.list_topics(timeout=10)
            if topic_name in metadata.topics:
                logger.info(f"Topic {topic_name} already exists")
                return True

            topic = NewTopic(
                topic_name,
                num_partitions=partitions,
                replication_factor=replication_factor,
            )

            fs = self.admin_client.create_topics([topic])
            fs[topic_name].result(timeout=10)
            logger.info(f"Topic {topic_name} created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create topic {topic_name}: {e}")
            return False

    async def ensure_cache_topics_exist(self) -> bool:
        """Ensure all required cache-related topics exist.

        Returns:
            bool: True if all topics exist or were created successfully.
        """
        topics = [(settings.KAFKA_CACHE_INVALIDATION_TOPIC, 1, 1)]

        results = []
        for topic_name, partitions, replication in topics:
            result = await self.ensure_topic_exists(
                topic_name, partitions, replication
            )
            results.append(result)

        return all(results)


kafka_topic_manager = KafkaTopicManager()
