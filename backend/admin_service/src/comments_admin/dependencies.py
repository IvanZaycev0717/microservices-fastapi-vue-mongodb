from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_db_session(request: Request):
    """
    Dependency that provides database session using app's engine
    """
    async with request.app.state.postgres_engine.begin() as conn:
        session = async_sessionmaker(
            conn, class_=AsyncSession, expire_on_commit=False
        )()
        try:
            yield session
        finally:
            await session.close()
