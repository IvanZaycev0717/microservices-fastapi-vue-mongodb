import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from logger import get_logger
from services.database import db_manager
from services.kafka_consumer import kafka_consumer
from settings import settings

logger = get_logger(f"{settings.NOTIFICATION_SERVICE_NAME} - Main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for FastAPI application."""
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
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.NOTIFICATION_SERVICE_NAME,
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"{settings.NOTIFICATION_SERVICE_NAME} is running"}


if __name__ == "__main__":
    uvicorn.run(
        app, host=settings.NOTIFICATION_HOST, port=settings.NOTIFICATION_PORT
    )
