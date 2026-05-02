"""Database engine and session configuration.

Initializes the async SQLAlchemy engine and session factory,
and provides a dependency for obtaining database sessions.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend_common.database.engine import create_engine, create_session_factory
from src.app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
AsyncSessionLocal = create_session_factory(engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session and ensure cleanup on exit.

    Yields:
        An async SQLAlchemy session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
