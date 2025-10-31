import asyncio
import logging

from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from settings import settings

logger = logging.getLogger("KafkaTopics")


async def wait_for_kafka_ready(
    max_retries: int = 30, retry_delay: int = 2
) -> None:
    """Wait for Kafka cluster to be fully ready using aiokafka.

    Args:
        max_retries: Maximum number of connection attempts.
        retry_delay: Delay between retries in seconds.

    Raises:
        Exception: If Kafka cluster is not ready after max_retries.
    """
    logger.info("Waiting for Kafka cluster to be ready...")

    for attempt in range(max_retries):
        try:
            admin = AIOKafkaAdminClient(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                request_timeout_ms=5000,
            )

            await admin.start()
            await admin.list_topics()
            await admin.close()

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


async def create_kafka_topics():
    """Create necessary Kafka topics on startup using aiokafka.

    Creates topics with recommended partitioning and replication.
    Safe to run multiple times - topics won't be recreated if they exist.
    """
    await wait_for_kafka_ready()

    admin = AIOKafkaAdminClient(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )

    topics = [
        NewTopic(
            name=settings.KAFKA_PASSWORD_RESET_TOPIC,
            num_partitions=3,
            replication_factor=1,
        ),
        NewTopic(
            name=settings.KAFKA_PASSWORD_RESET_SUCCESS_TOPIC,
            num_partitions=3,
            replication_factor=1,
        ),
    ]

    try:
        await admin.start()

        existing_topics = await admin.list_topics()
        topics_to_create = [
            topic for topic in topics if topic.name not in existing_topics
        ]

        if topics_to_create:
            await admin.create_topics(
                new_topics=topics_to_create,
                validate_only=False,
            )
            logger.info("Kafka topics created successfully")
        else:
            logger.info("Kafka topics already exist")

    except Exception as e:
        logger.warning(f"Kafka topics creation issue: {e}")
    finally:
        await admin.close()


async def ensure_topics_exist():
    """Ensure required Kafka topics exist using async aiokafka."""
    await create_kafka_topics()
