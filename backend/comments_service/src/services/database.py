from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from logger import get_logger
from settings import settings

logger = get_logger("database")

engine = create_async_engine(
    settings.GRPC_COMMENTS_POSTGRES_URL.get_secret_value(),
    pool_size=settings.POSTGRES_POOL_MAX_SIZE,
    max_overflow=0,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@asynccontextmanager
async def get_db_session() -> AsyncSession:
    """Async context manager for database session handling.

    Provides a managed database session that automatically handles
    cleanup and closure.

    Yields:
        AsyncSession: An active database session.

    Note:
        - Ensures session is properly closed even if exceptions occur
        - Suitable for use with async context managers (async with)
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def init_db():
    """Initializes database connection and verifies connectivity.

    Tests the database connection by executing a simple query to ensure
    the database is accessible and responsive.

    Raises:
        Exception: If database connection fails.

    Note:
        - Performs a basic health check with 'SELECT 1' query
        - Logs successful connection or failure details
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.commit()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


async def close_db():
    """Closes database connection and releases resources.

    Disposes of the database engine connection pool and cleans up
    all database connections.

    Note:
        - Properly disposes of connection pool to prevent resource leaks
        - Should be called during application shutdown
    """
    await engine.dispose()
    logger.info("Database connection closed")
