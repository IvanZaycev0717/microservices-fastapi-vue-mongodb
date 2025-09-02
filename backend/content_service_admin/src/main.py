from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from services.db_management import (
    MongoCollectionsManager,
    MongoConnectionManager,
    MongoDatabaseManager,
)
from services.logger import get_logger
from settings import settings

logger = get_logger("main")

MONGODB_HOST = settings.MONGODB_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_connection = MongoConnectionManager(host=MONGODB_HOST)
    try:
        client = await mongo_connection.open_connection()
        database_manager = MongoDatabaseManager(client)
        if not await database_manager.check_database_existence(settings.MONGO_DB_NAME):
            db = await database_manager.create_database(settings.MONGO_DB_NAME)
        else:
            db = client[settings.MONGO_DB_NAME]
        mongo_collections_manager = MongoCollectionsManager(client, db)
        await mongo_collections_manager.initialize_collections()
    except Exception:
        logger.error("Failed to connect to MongoDB")
    yield
    await mongo_connection.close_connection()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Content Service",
    description="Microservice for content management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(
            f"Response: {response.status_code}for {request.method} {request.url}"
        )
        return response
    except Exception as e:
        logger.error(f"Error processing request {request.method} {request.url}: {e}")
        raise


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Content Service is running"}


@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    try:
        logger.info("Health check: MongoDB connection OK")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
