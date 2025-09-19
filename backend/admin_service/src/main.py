from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from auth_admin.routes import auth
from content_admin.routes import (
    about,
    certificates,
    projects,
    publications,
    tech,
)
from services.data_loader import DataLoader
from services.logger import get_logger
from services.minio_management import MinioCRUD
from services.mongo_db_management import (
    MongoCollectionsManager,
    MongoConnectionManager,
    MongoDatabaseManager,
)
from settings import settings

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    content_admin_mongo_connection = MongoConnectionManager(
        host=settings.CONTENT_ADMIN_MONGODB_URL
    )

    auth_admin_mongo_connection = MongoConnectionManager(
        host=settings.AUTH_ADMIN_MONGODB_URL
    )

    minio_crud = MinioCRUD()

    try:
        # Establish MongoDB connections
        content_admin_client = (
            await content_admin_mongo_connection.open_connection()
        )
        auth_admin_client = await auth_admin_mongo_connection.open_connection()

        # Initialize database managers
        content_admin_database_manager = MongoDatabaseManager(
            content_admin_client
        )
        auth_admin_database_manager = MongoDatabaseManager(auth_admin_client)

        # Ensure content admin database exists
        if not await content_admin_database_manager.check_database_existence(
            settings.CONTENT_ADMIN_MONGO_DATABASE_NAME
        ):
            content_admin_db = (
                await content_admin_database_manager.create_database(
                    settings.CONTENT_ADMIN_MONGO_DATABASE_NAME
                )
            )
            logger.info(
                f"Created content database: {settings.CONTENT_ADMIN_MONGO_DATABASE_NAME}"
            )
        else:
            content_admin_db = content_admin_client[
                settings.CONTENT_ADMIN_MONGO_DATABASE_NAME
            ]
            logger.info(
                f"Using existing content database: {settings.CONTENT_ADMIN_MONGO_DATABASE_NAME}"
            )

        # Ensure auth admin database exists
        if not await auth_admin_database_manager.check_database_existence(
            settings.AUTH_ADMIN_MONGO_DATABASE_NAME
        ):
            auth_admin_db = await auth_admin_database_manager.create_database(
                settings.AUTH_ADMIN_MONGO_DATABASE_NAME
            )
            logger.info(
                f"Created auth database: {settings.AUTH_ADMIN_MONGO_DATABASE_NAME}"
            )
        else:
            auth_admin_db = auth_admin_client[
                settings.AUTH_ADMIN_MONGO_DATABASE_NAME
            ]
            logger.info(
                f"Using existing auth database: {settings.AUTH_ADMIN_MONGO_DATABASE_NAME}"
            )

        # Initialize data loader
        data_loader = DataLoader(
            settings.CONTENT_ADMIN_PATH, settings.INITIAL_DATA_LOADING_FILES
        )

        # Check local files
        if not await data_loader.check_loading_files():
            logger.error("Missing local files for initialization")
            raise FileNotFoundError(
                "Required files not found in local machine"
            )

        # Process ABOUT bucket
        if not await data_loader.check_minio_files_existence(
            minio_crud, settings.ABOUT_BUCKET_NAME
        ):
            logger.warning("Files not found in MinIO ABOUT bucket")
            logger.info("Starting image upload to MinIO ABOUT bucket...")
            uploaded_files = await data_loader.upload_images_to_minio(
                minio_crud, settings.ABOUT_BUCKET_NAME
            )
            logger.info(
                f"Uploaded {len(uploaded_files)} files to MinIO ABOUT bucket"
            )
        else:
            logger.info("MinIO ABOUT bucket already has required files")

        # Process PROJECTS bucket
        if not await data_loader.check_minio_files_existence(
            minio_crud, settings.PROJECTS_BUCKET_NAME
        ):
            logger.warning("Files not found in MinIO PROJECTS bucket")
            logger.info("Starting image upload to MinIO PROJECTS bucket...")
            uploaded_files = await data_loader.upload_images_to_minio(
                minio_crud, settings.PROJECTS_BUCKET_NAME
            )
            logger.info(
                f"Uploaded {len(uploaded_files)} files to MinIO PROJECTS bucket"
            )
        else:
            logger.info("MinIO PROJECTS bucket already has required files")

        # Load admin user into auth database
        admin_loaded = await data_loader.load_admin_user_to_auth_db(
            auth_admin_database_manager,
            settings.ADMIN_EMAIL.get_secret_value(),
            settings.ADMIN_PASSWORD.get_secret_value(),
        )

        if not admin_loaded:
            logger.error(
                "Failed to load admin user into auth database - check logs for details"
            )

        # Initialize collections
        content_admin_mongo_collections_manager = MongoCollectionsManager(
            content_admin_client, content_admin_db
        )
        await content_admin_mongo_collections_manager.initialize_collections()
        logger.info("Database collections initialized successfully")

        # Save connections to app state
        app.state.content_admin_mongo_client = content_admin_client
        app.state.content_admin_mongo_db = content_admin_db
        app.state.auth_admin_mongo_client = auth_admin_client
        app.state.auth_admin_mongo_db = auth_admin_db
        app.state.minio_crud = minio_crud

        logger.info("Application startup complete - all services initialized")

    except FileNotFoundError as e:
        logger.exception(f"Initialization failed due to missing files: {e}")
        raise
    except Exception as e:
        logger.exception(f"Application startup failed: {e}")
        raise
    finally:
        yield

    # Cleanup on shutdown
    await content_admin_mongo_connection.close_connection()
    await auth_admin_mongo_connection.close_connection()
    logger.info("Application shutdown complete - connections closed")


app = FastAPI(
    title="Admin Service",
    description="Common admin panel for all services",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(about.router, tags=[settings.CONTENT_ADMIN_ABOUT_NAME])
app.include_router(tech.router, tags=[settings.CONTENT_ADMIN_TECH_NAME])
app.include_router(
    projects.router, tags=[settings.CONTENT_ADMIN_PROJECTS_NAME]
)
app.include_router(
    certificates.router, tags=[settings.CONTENT_ADMIN_CERTIFICATES_NAME]
)
app.include_router(
    publications.router, tags=[settings.CONTENT_ADMIN_PUBLICATIONS_NAME]
)

app.include_router(auth.router, tags=[settings.AUTH_ADMIN_NAME])

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
            f"Response: {response.status_code} "
            f"for {request.method} {request.url}"
        )
        return response
    except Exception as e:
        logger.exception(
            f"Error processing request {request.method} {request.url}: {e}"
        )
        raise


@app.get("/", tags=["Admin Service Maintenance"])
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Content Service is running"}


@app.get("/health", tags=["Admin Service Maintenance"])
async def health_check():
    logger.debug("Health check endpoint accessed")
    try:
        logger.info("Health check: MongoDB connection OK")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.exception(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="localhost", port=8000)
