import asyncio

from fastapi import Request

from services.logger import get_logger

logger = get_logger("CacheInvalidation")


async def send_cache_invalidation(
    request: Request,
    entity_type: str,
    action: str,
    entity_id: str | None = None,
) -> bool:
    """Send cache invalidation event to Kafka.

    Non-blocking - fires and forgets to avoid delaying HTTP response.
    """
    try:
        kafka_producer = request.app.state.kafka_producer

        asyncio.create_task(
            _send_cache_invalidation_async(
                kafka_producer, entity_type, action, entity_id
            )
        )

        logger.debug(
            f"Cache invalidation queued: {entity_type}.{action}.{entity_id or 'all'}"
        )
        return True

    except Exception as e:
        logger.error(f"Error queueing cache invalidation: {e}")
        return False


async def _send_cache_invalidation_async(
    kafka_producer, entity_type: str, action: str, entity_id: str | None = None
):
    """Background task to send cache invalidation without blocking."""
    try:
        success = await kafka_producer.send_cache_invalidation(
            entity_type, action, entity_id
        )

        if success:
            logger.debug(
                f"Cache invalidation delivered: {entity_type}.{action}.{entity_id or 'all'}"
            )
        else:
            logger.warning(
                f"Failed to deliver cache invalidation: {entity_type}.{action}.{entity_id or 'all'}"
            )

    except Exception as e:
        logger.error(f"Error in background cache invalidation: {e}")
