from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from logger import get_logger
from settings import settings

logger = get_logger(f"{settings.GRPC_COMMENTS_SERVICE_NAME} - database")

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
    """Get async database session."""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()

async def init_db():
    """Initialize database connection and verify it works."""
    try:
        async with engine.connect() as conn:
            # Используем text() для сырых SQL выражений в SQLAlchemy 2.0
            await conn.execute(text("SELECT 1"))
            await conn.commit()  # Явный коммит для соединения
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

async def close_db():
    """Close database connection."""
    await engine.dispose()
    logger.info("Database connection closed")