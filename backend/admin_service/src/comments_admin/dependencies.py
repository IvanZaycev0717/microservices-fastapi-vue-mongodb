from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_db_session(request: Request):
    """Get async database session for PostgreSQL.

    Args:
        request: FastAPI Request object containing application state.

    Yields:
        AsyncSession: Async database session for comments operations.
    """
    async with request.app.state.postgres_engine.begin() as conn:
        session = async_sessionmaker(
            conn, class_=AsyncSession, expire_on_commit=False
        )()
        try:
            yield session
        finally:
            await session.close()
