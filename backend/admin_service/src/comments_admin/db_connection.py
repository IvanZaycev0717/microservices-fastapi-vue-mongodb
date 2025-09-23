from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from settings import settings


def get_engine():
    return create_async_engine(settings.COMMENTS_ADMIN_POSTGRES_DB_URL)


AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=get_engine(), class_=AsyncSession
)


async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session
