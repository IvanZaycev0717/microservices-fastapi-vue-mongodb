from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from content_admin.routes import about, tech
from services.mongo_db_management import (
    MongoCollectionsManager,
    MongoConnectionManager,
    MongoDatabaseManager,
)
from services.logger import get_logger
from settings import settings
from services.data_loader import DataLoader
from services.minio_management import MinioCRUD

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    content_admin_mongo_connection = MongoConnectionManager(
        host=settings.CONTENT_ADMIN_MONGODB_URL
    )

    minio_crud = MinioCRUD()
    try:
        content_admin_client = await content_admin_mongo_connection.open_connection()
        content_admin_database_manager = MongoDatabaseManager(content_admin_client)
        if not await content_admin_database_manager.check_database_existence(
            settings.CONTENT_ADMIN_MONGO_DATABASE_NAME
        ):
            content_admin_db = await content_admin_database_manager.create_database(
                settings.CONTENT_ADMIN_MONGO_DATABASE_NAME
            )
        else:
            content_admin_db = content_admin_client[
                settings.CONTENT_ADMIN_MONGO_DATABASE_NAME
            ]

        data_loader = DataLoader(
            settings.CONTENT_ADMIN_PATH, settings.INITIAL_DATA_LOADING_FILES
        )
        if not await data_loader.check_loading_files():
            logger.warning("Missing local files")
            raise FileNotFoundError("Files not found in local machine")
        if not await data_loader.check_minio_files_existence(
            minio_crud, settings.ABOUT_BUCKET_NAME
        ):
            logger.warning("Files not found in MinIO")
            logger.info("Starting image upload to MinIO...")
            uploaded_files = await data_loader.upload_images_to_minio(
                minio_crud, settings.ABOUT_BUCKET_NAME
            )
            logger.info(f"{uploaded_files} was upload to MinIO")
        else:
            logger.info("MinIO already has required files")

        app.state.content_admin_mongo_client = content_admin_client
        app.state.content_admin_mongo_db = content_admin_db

        content_admin_mongo_collections_manager = MongoCollectionsManager(
            content_admin_client, content_admin_db
        )

        await content_admin_mongo_collections_manager.initialize_collections()

    except FileNotFoundError as e:
        logger.error(e)
    except Exception:
        logger.error("Failed to connect to MongoDB")
    yield
    await content_admin_mongo_connection.close_connection()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Admin Service",
    description="Common admin panel for all services",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(about.router, tags=["Content Service"])
app.include_router(tech.router, tags=["Content Service"])

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
    uvicorn.run(app, host="localhost", port=8000)
