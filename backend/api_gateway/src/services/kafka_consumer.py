import json
import threading
import asyncio
from confluent_kafka import Consumer, KafkaError
from logger import get_logger
from services.redis_connect_management import RedisDatabase
from services.cache_service import CacheService
from settings import settings

logger = get_logger("KafkaConsumer")


class KafkaCacheInvalidationConsumer:
    """Kafka consumer running in background thread with async message processing."""

    def __init__(self):
        self.consumer = None
        self.running = False
        self.thread = None
        self.message_queue = asyncio.Queue()
        self.redis_manager = None
        self.main_loop = None

    async def _wait_for_kafka(self, timeout: int = 30) -> bool:
        """Wait for Kafka brokers to become available asynchronously.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            bool: True if Kafka is available, False if timeout exceeded.
        """
        start_time = asyncio.get_event_loop().time()
        logger.info("Waiting for Kafka brokers to become available...")

        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                success = await asyncio.get_event_loop().run_in_executor(
                    None, self._check_kafka_connection
                )

                if success:
                    logger.info("Kafka brokers are now available")
                    return True

            except Exception as e:
                logger.debug(f"Kafka check failed: {e}")

            await asyncio.sleep(2)

        logger.warning(
            "Kafka brokers not available after timeout, continuing anyway..."
        )
        return False

    def _check_kafka_connection(self) -> bool:
        """Synchronous Kafka connection check to run in thread pool.

        Returns:
            bool: True if Kafka is reachable and topic exists.
        """
        try:
            consumer = Consumer(
                {
                    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                    "group.id": "health-check",
                    "session.timeout.ms": 10000,
                }
            )

            metadata = consumer.list_topics(
                settings.KAFKA_CACHE_INVALIDATION_TOPIC, timeout=10
            )
            consumer.close()

            topic_metadata = metadata.topics.get(
                settings.KAFKA_CACHE_INVALIDATION_TOPIC
            )
            if topic_metadata and not topic_metadata.error:
                logger.info(
                    f"Topic {settings.KAFKA_CACHE_INVALIDATION_TOPIC} is available"
                )
                return True
            else:
                logger.warning(
                    f"Topic {settings.KAFKA_CACHE_INVALIDATION_TOPIC} not found"
                )
                return False

        except Exception as e:
            logger.debug(f"Kafka connection check failed: {e}")
            return False

    async def start(self, redis_manager):
        """Start the Kafka consumer in background thread."""
        self.redis_manager = redis_manager
        self.main_loop = asyncio.get_running_loop()

        await self._wait_for_kafka()

        self.running = True
        self.thread = threading.Thread(target=self._consume_messages)
        self.thread.daemon = True
        self.thread.start()

        asyncio.create_task(self._process_queued_messages())

        logger.info("Kafka consumer started in background thread")

    def _consume_messages(self):
        """Background thread function to consume Kafka messages."""
        try:
            self.consumer = Consumer(
                {
                    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                    "group.id": settings.KAFKA_CONSUMER_GROUP_ID,
                    "auto.offset.reset": settings.KAFKA_AUTO_OFFSET_RESET,
                    "enable.auto.commit": settings.KAFKA_ENABLE_AUTO_COMMIT,
                }
            )

            self.consumer.subscribe([settings.KAFKA_CACHE_INVALIDATION_TOPIC])

            while self.running:
                try:
                    msg = self.consumer.poll(1.0)

                    if msg is None:
                        continue
                    if msg.error():
                        # Correct Kafka error checking
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            continue
                        else:
                            logger.error(f"Consumer error: {msg.error()}")
                            continue

                    asyncio.run_coroutine_threadsafe(
                        self.message_queue.put(msg), self.main_loop
                    )

                except Exception as e:
                    logger.error(f"Error in consumer thread: {e}")

        except Exception as e:
            logger.exception(f"Fatal error in consumer thread: {e}")
        finally:
            if self.consumer:
                self.consumer.close()

    async def _process_queued_messages(self):
        """Async coroutine to process messages from the queue."""
        while self.running:
            try:
                msg = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )
                await self._process_message(msg)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.exception(f"Error processing queued message: {e}")

    async def _process_message(self, msg):
        """Process a single cache invalidation message."""
        try:
            message_data = json.loads(msg.value().decode("utf-8"))
            entity_type = message_data.get("entity_type")
            action = message_data.get("action")
            entity_id = message_data.get("entity_id")

            logger.info(
                f"Processing cache invalidation: {entity_type}.{action}.{entity_id or 'all'}"
            )

            cache_client = self.redis_manager.get_client(RedisDatabase.CACHE)
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
        """Stop the Kafka consumer."""
        self.running = False

        if self.thread:
            self.thread.join(timeout=5.0)

        logger.info("Kafka consumer stopped")


kafka_consumer = KafkaCacheInvalidationConsumer()
