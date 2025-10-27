import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from auth_admin.routes import auth
from comments_admin.models import Base
from comments_admin.routes import comments
from content_admin.routes import (
    about,
    certificates,
    projects,
    publications,
    tech,
)
from notification_admin.routes import notification
from services.data_loader import DataLoader
from services.kafka_producer import kafka_producer
from services.kafka_topic_management import kafka_topic_manager
from services.logger import get_logger
from services.minio_management import MinioCRUD
from services.mongo_db_management import (
    MongoCollectionsManager,
    MongoConnectionManager,
    MongoDatabaseManager,
)
from services.postgres_db_management import (
    PostgresConnectionManager,
    PostgresDatabaseManager,
)
from settings import settings

logger = get_logger("main")

engine = create_async_engine(settings.COMMENTS_ADMIN_POSTGRES_DB_URL)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connections = {}
    clients = {}
    databases = {}

    try:
        connections["content_admin"] = MongoConnectionManager(
            host=settings.CONTENT_ADMIN_MONGODB_URL
        )
        connections["auth_admin"] = MongoConnectionManager(
            host=settings.AUTH_ADMIN_MONGODB_URL
        )
        connections["notification_admin"] = MongoConnectionManager(
            host=settings.NOTIFICATION_ADMIN_MONGODB_URL
        )

        connections["comments_admin"] = PostgresConnectionManager(
            host=settings.COMMENTS_ADMIN_POSTGRES_ROOT_NAME,
            port=settings.COMMENTS_ADMIN_POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database="postgres",
        )

        (
            clients["content_admin"],
            databases["content_admin"],
        ) = await ensure_mongo_database(
            connections["content_admin"],
            settings.CONTENT_ADMIN_MONGO_DATABASE_NAME,
            "content admin",
        )

        (
            clients["auth_admin"],
            databases["auth_admin"],
        ) = await ensure_mongo_database(
            connections["auth_admin"],
            settings.AUTH_ADMIN_MONGO_DATABASE_NAME,
            "auth admin",
        )

        (
            clients["notification_admin"],
            databases["notification_admin"],
        ) = await ensure_mongo_database(
            connections["notification_admin"],
            settings.NOTIFICATION_ADMIN_MONGO_DATABASE_NAME,
            "notification admin",
        )

        comments_admin_client = await connections[
            "comments_admin"
        ].open_connection()
        comments_admin_db_manager = PostgresDatabaseManager(
            comments_admin_client
        )

        if not await comments_admin_db_manager.check_database_existence(
            settings.COMMENTS_ADMIN_POSTGRES_DB_NAME
        ):
            success = await comments_admin_db_manager.create_database(
                settings.COMMENTS_ADMIN_POSTGRES_DB_NAME,
                settings.COMMENTS_ADMIN_POSTGRES_ROOT_NAME,
                settings.COMMENTS_ADMIN_POSTGRES_PORT,
                settings.POSTGRES_USER,
                settings.POSTGRES_PASSWORD,
            )
            if success:
                logger.info(
                    f"Created comments database: {settings.COMMENTS_ADMIN_POSTGRES_DB_NAME}"
                )
            else:
                logger.exception(
                    f"Failed to create comments database: {settings.COMMENTS_ADMIN_POSTGRES_DB_NAME}"
                )
                raise Exception("PostgreSQL database creation failed")
        else:
            logger.info(
                f"Using existing comments database: {settings.COMMENTS_ADMIN_POSTGRES_DB_NAME}"
            )

        await connections["comments_admin"].close_connection()

        connections["comments_admin"] = PostgresConnectionManager(
            host=settings.COMMENTS_ADMIN_POSTGRES_ROOT_NAME,
            port=settings.COMMENTS_ADMIN_POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.COMMENTS_ADMIN_POSTGRES_DB_NAME,  # ← теперь к нашей БД
        )

        comments_admin_client = await connections[
            "comments_admin"
        ].open_connection()

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Comments database tables created successfully")

        minio_crud = MinioCRUD()

        
        data_loader = DataLoader(
            settings.CONTENT_ADMIN_PATH, settings.INITIAL_DATA_LOADING_FILES
        )

        if not await data_loader.check_loading_files():
            logger.error("Missing local files for initialization")
            raise FileNotFoundError(
                "Required files not found in local machine"
            )

        buckets = [
            (settings.ABOUT_BUCKET_NAME, "ABOUT"),
            (settings.PROJECTS_BUCKET_NAME, "PROJECTS"),
            (settings.CERTIFICATES_BUCKET_NAME, "CERTIFICATES")
        ]

        for bucket_name, bucket_type in buckets:
            await minio_crud.create_bucket_if_not_exists(bucket_name)

        for bucket_name, bucket_type in buckets:
            if not await data_loader.check_minio_files_existence(
                minio_crud, bucket_name
            ):
                logger.warning(
                    f"Files not found in MinIO {bucket_type} bucket"
                )
                logger.info(
                    f"Starting image upload to MinIO {bucket_type} bucket..."
                )
                uploaded_files = await data_loader.upload_images_to_minio(
                    minio_crud, bucket_name
                )
                logger.info(
                    f"Uploaded {len(uploaded_files)} files to MinIO {bucket_type} bucket"
                )
            else:
                logger.info(
                    f"MinIO {bucket_type} bucket already has required files"
                )

        auth_admin_db_manager = MongoDatabaseManager(clients["auth_admin"])
        admin_loaded = await data_loader.load_admin_user_to_auth_db(
            auth_admin_db_manager,
            settings.ADMIN_EMAIL.get_secret_value(),
            settings.ADMIN_PASSWORD.get_secret_value(),
        )

        if not admin_loaded:
            logger.error(
                "Failed to load admin user into auth database - check logs for details"
            )
        else:
            logger.info("Admin user loaded successfully")

        content_admin_mongo_collections_manager = MongoCollectionsManager(
            clients["content_admin"], databases["content_admin"]
        )
        await content_admin_mongo_collections_manager.initialize_collections()
        logger.info(
            "Content admin database collections initialized successfully"
        )

        await kafka_topic_manager.ensure_cache_topics_exist()
        await kafka_producer.connect()

        # Content states
        app.state.content_admin_mongo_client = clients["content_admin"]
        app.state.content_admin_mongo_db = databases["content_admin"]

        # Auth states
        app.state.auth_admin_mongo_client = clients["auth_admin"]
        app.state.auth_admin_mongo_db = databases["auth_admin"]

        # Comments states
        app.state.postgres_engine = engine
        app.state.comments_admin_client = comments_admin_client  # ← добавляем

        # Notifications states
        app.state.notification_admin_client = clients["notification_admin"]
        app.state.notification_admin_db = databases["notification_admin"]

        # Minio States
        app.state.minio_crud = minio_crud

        # Kafka States
        app.state.kafka_producer = kafka_producer

        logger.info("Application startup complete - all services initialized")
        yield

    except Exception as e:
        logger.exception(f"Application startup failed: {e}")
        raise

    finally:
        close_tasks = []

        for name, connection in connections.items():
            if connection:
                close_tasks.append(connection.close_connection())

        if "engine" in locals():
            await engine.dispose()

        close_tasks.append(kafka_producer.close())

        if close_tasks:
            results = await asyncio.gather(
                *close_tasks, return_exceptions=True
            )
            for result in results:
                if isinstance(result, Exception):
                    logger.warning(f"Error during connection close: {result}")

        logger.info("Application shutdown complete - all connections closed")


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

app.include_router(comments.router, tags=[settings.COMMENTS_ADMIN_NAME])

app.include_router(
    notification.router, tags=[settings.NOTIFICATION_ADMIN_NAME]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log HTTP requests and responses.

    Args:
        request: Incoming HTTP request.
        call_next: Next middleware or route handler.

    Returns:
        Response: HTTP response from the next handler.

    Raises:
        Exception: Re-raises any exceptions from the request processing.
    """
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
    """Root endpoint for service health check.

    Returns:
        dict: Service status message.
    """
    logger.info("Root endpoint accessed")
    return {"message": "Content Service is running"}


@app.get("/health", tags=["Admin Service Maintenance"])
async def health_check():
    """Health check endpoint for service monitoring.

    Returns:
        dict: Service health status and database connection state.
    """
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


async def ensure_mongo_database(
    connection_manager: MongoConnectionManager, db_name: str, manager_name: str
):
    """Ensure MongoDB database exists and return client and database instances.

    Args:
        connection_manager (MongoConnectionManager): MongoDB connection manager.
        db_name (str): Name of the database to ensure.
        manager_name (str): Descriptive name for the database manager.

    Returns:
        tuple: MongoDB client and database instances.

    Raises:
        Exception: If database creation or connection fails.
    """
    client = None
    try:
        client = await connection_manager.open_connection()
        db_manager = MongoDatabaseManager(client)

        database_list = await db_manager.get_database_list()

        if db_name not in database_list:
            db = await db_manager.create_database(db_name)
            logger.info(f"Created {manager_name} database: {db_name}")
        else:
            db = client[db_name]
            logger.info(f"Using existing {manager_name} database: {db_name}")

        return client, db

    except Exception as e:
        logger.error(f"Error ensuring MongoDB database {db_name}: {e}")
        if client:
            await connection_manager.close_connection()
        raise
