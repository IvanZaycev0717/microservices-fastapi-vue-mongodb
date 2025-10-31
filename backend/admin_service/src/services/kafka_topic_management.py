# src/services/kafka_topic_management.py
import asyncio
import logging

from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from settings import settings

logger = logging.getLogger("KafkaTopicManager")


class KafkaTopicManager:
    """Manager for Kafka topics using aiokafka."""

    def __init__(self):
        self.admin_client: AIOKafkaAdminClient | None = None

    async def ensure_cache_topics_exist(self):
        """Ensure required Kafka topics for cache invalidation exist."""
        await self._wait_for_kafka_ready()
        await self._create_topics()

    async def _wait_for_kafka_ready(
        self, max_retries: int = 30, retry_delay: int = 2
    ) -> None:
        """Wait for Kafka cluster to be fully ready."""
        logger.info("Waiting for Kafka cluster to be ready...")

        for attempt in range(max_retries):
            try:
                self.admin_client = AIOKafkaAdminClient(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    request_timeout_ms=5000,
                )
                
                await self.admin_client.start()
                await self.admin_client.list_topics()
                logger.info("Kafka cluster is ready")
                return

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Kafka not ready (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("Kafka cluster failed to become ready")
                    raise
            finally:
                if self.admin_client:
                    await self.admin_client.close()
                    self.admin_client = None

    async def _create_topics(self):
        """Create necessary Kafka topics."""
        self.admin_client = AIOKafkaAdminClient(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )

        topics = [
            NewTopic(
                name=settings.KAFKA_CACHE_INVALIDATION_TOPIC,
                num_partitions=3,
                replication_factor=1,
            ),
            NewTopic(
                name=settings.KAFKA_LOGS_TOPIC,
                num_partitions=3,
                replication_factor=1,
            ),
        ]

        try:
            await self.admin_client.start()
            
            # Проверяем существующие топики
            existing_topics = await self.admin_client.list_topics()
            topics_to_create = [
                topic for topic in topics if topic.name not in existing_topics
            ]
            
            if topics_to_create:
                await self.admin_client.create_topics(
                    new_topics=topics_to_create,
                    validate_only=False,
                )
                logger.info("Kafka topics created successfully")
            else:
                logger.info("Kafka topics already exist")
                
        except Exception as e:
            logger.warning(f"Kafka topics creation issue: {e}")
        finally:
            await self.admin_client.close()

    async def close(self):
        """Close admin client connection."""
        if self.admin_client:
            await self.admin_client.close()
            logger.info("Kafka topic manager closed")


kafka_topic_manager = KafkaTopicManager()