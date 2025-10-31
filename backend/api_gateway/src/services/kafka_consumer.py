import json
import asyncio
from aiokafka import AIOKafkaConsumer
from logger import get_logger
from services.redis_connect_management import RedisDatabase
from services.cache_service import CacheService
from settings import settings

logger = get_logger("KafkaConsumer")


class KafkaCacheInvalidationConsumer:
    """Kafka consumer for cache invalidation messages using aiokafka.

    This consumer listens for cache invalidation events and clears corresponding
    Redis cache entries based on entity type patterns.

    Attributes:
        consumer: AIOKafkaConsumer instance for message consumption.
        running: Boolean flag indicating if consumer is active.
        redis_manager: RedisManager instance for cache operations.
        _consume_task: Asyncio task for message consumption loop.
    """

    def __init__(self):
        """Initializes KafkaCacheInvalidationConsumer with default state."""
        self.consumer = None
        self.running = False
        self.redis_manager = None
        self._consume_task = None

    async def start(self, redis_manager):
        """Starts the Kafka consumer and begins message processing.

        Args:
            redis_manager: RedisManager instance for cache operations.

        Raises:
            Exception: If Kafka consumer fails to start.
        """
        self.redis_manager = redis_manager
        self.running = True

        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_CACHE_INVALIDATION_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP_ID,
            auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
            enable_auto_commit=settings.KAFKA_ENABLE_AUTO_COMMIT,
        )

        await self.consumer.start()
        self._consume_task = asyncio.create_task(self._consume_messages())

        logger.info("Kafka consumer started with aiokafka")

    async def _consume_messages(self):
        """Consumes messages from Kafka topic using async iterator.

        Continuously polls for new messages and processes them until stopped.
        Automatically handles consumer stopping on exit.
        """
        try:
            async for msg in self.consumer:
                if not self.running:
                    break
                await self._process_message(msg)
        except Exception as e:
            logger.exception(f"Error in consumer: {e}")
        finally:
            await self.consumer.stop()

    async def _process_message(self, msg):
        """Processes a single cache invalidation message.

        Args:
            msg: Raw Kafka message containing cache invalidation data.

        Steps:
            1. Parses JSON message payload
            2. Extracts entity type and action information
            3. Clears Redis cache entries matching entity pattern
        """
        try:
            message_data = json.loads(msg.value.decode("utf-8"))
            entity_type = message_data.get("entity_type")
            action = message_data.get("action")
            entity_id = message_data.get("entity_id")

            logger.info(
                f"Processing cache invalidation: {entity_type}.{action}.{entity_id or 'all'}"
            )

            cache_client = await self.redis_manager.get_client(
                RedisDatabase.CACHE
            )
            cache_service = CacheService(cache_client)

            pattern = f"content:*{entity_type}*"
            logger.info(f"Attempting to clear cache with pattern: {pattern}")

            success = await cache_service.clear_pattern(pattern)

            if success:
                logger.info(
                    f"Cache invalidated successfully for pattern: {pattern}"
                )
            else:
                logger.error(
                    f"Failed to invalidate cache for pattern: {pattern}"
                )

        except Exception as e:
            logger.exception(f"Error processing Kafka message: {e}")

    async def stop(self):
        """Stops the Kafka consumer gracefully.

        Cancels the consumption task and ensures clean shutdown.
        """
        self.running = False

        if self._consume_task:
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                pass

        logger.info("Kafka consumer stopped")


kafka_consumer = KafkaCacheInvalidationConsumer()
