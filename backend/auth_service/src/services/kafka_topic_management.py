import asyncio
import logging

from confluent_kafka.admin import AdminClient, NewTopic

from settings import settings

logger = logging.getLogger(f"{settings.GRPC_AUTH_NAME} - KafkaTopics")


async def wait_for_kafka_ready(
    max_retries: int = 30, retry_delay: int = 2
) -> None:
    """Wait for Kafka cluster to be fully ready.

    Args:
        max_retries: Maximum number of connection attempts.
        retry_delay: Delay between retries in seconds.

    Raises:
        Exception: If Kafka cluster is not ready after max_retries.
    """
    logger.info("Waiting for Kafka cluster to be ready...")

    for attempt in range(max_retries):
        try:
            admin = AdminClient(
                {
                    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                    "socket.timeout.ms": 5000,
                    "metadata.request.timeout.ms": 5000,
                }
            )

            # Try to list topics - this validates cluster connectivity
            admin.list_topics(timeout=5)
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
    """Create necessary Kafka topics on startup.

    Creates topics with recommended partitioning and replication.
    Safe to run multiple times - topics won't be recreated if they exist.
    """
    # Wait for cluster first
    await wait_for_kafka_ready()

    admin = AdminClient(
        {"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS}
    )

    topics = [
        NewTopic(
            settings.KAFKA_PASSWORD_RESET_TOPIC,
            num_partitions=3,
            replication_factor=1,
        )
    ]

    try:
        fs = admin.create_topics(topics)
        for topic, f in fs.items():
            f.result()  # Wait for topic creation
        logger.info("Kafka topics created successfully")
    except Exception as e:
        logger.warning(f"Kafka topics may already exist: {e}")


async def ensure_topics_exist():
    """Ensure required Kafka topics exist."""
    await create_kafka_topics()
