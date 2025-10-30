import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from logger import get_logger
from services.database import db_manager
from services.kafka_consumer import kafka_consumer
from settings import settings

logger = get_logger("Main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for notification service.

    Handles application startup and shutdown events including database
    connection, Kafka consumer initialization, and resource cleanup.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control passes to the application runtime.

    Raises:
        Exception: If startup initialization fails.

    Note:
        - Establishes database connection and Kafka consumer on startup
        - Begins consuming Kafka messages immediately after initialization
        - Ensures proper cleanup of Kafka consumer and database on shutdown
        - Logs service lifecycle events for monitoring
    """
    try:
        await db_manager.connect()
        await kafka_consumer.initialize()

        await kafka_consumer.consume_messages()

        logger.info(
            f"{settings.NOTIFICATION_SERVICE_NAME} started successfully"
        )
        logger.info(
            f"Server running on {settings.NOTIFICATION_HOST}:{settings.NOTIFICATION_PORT}"
        )

    except Exception as e:
        logger.error(
            f"Failed to start {settings.NOTIFICATION_SERVICE_NAME}: {e}"
        )
        raise

    yield

    try:
        await kafka_consumer.stop()
        await db_manager.disconnect()
        logger.info(
            f"{settings.NOTIFICATION_SERVICE_NAME} shut down successfully"
        )
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(title=settings.NOTIFICATION_SERVICE_NAME, lifespan=lifespan)


@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring.

    Returns:
        dict: Health status information containing:
            - status: Service health status
            - service: Name of the service
            - version: Service version number

    Note:
        - Used by load balancers and monitoring systems
        - Returns simple JSON response with service metadata
        - Always returns 'healthy' status when endpoint is reachable
    """
    return {
        "status": "healthy",
        "service": settings.NOTIFICATION_SERVICE_NAME,
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint for service verification.

    Returns:
        dict: Simple confirmation message indicating the service is running.

    Note:
        - Provides basic service status verification
        - Returns service name from application settings
    """
    return {"message": f"{settings.NOTIFICATION_SERVICE_NAME} is running"}


if __name__ == "__main__":
    uvicorn.run(
        app, host=settings.NOTIFICATION_HOST, port=settings.NOTIFICATION_PORT
    )
