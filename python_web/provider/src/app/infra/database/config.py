"""Database configuration and session management.

Initializes the SQLAlchemy async engine and session factory, and provides
a dependency for obtaining database sessions with automatic commit/rollback.
"""

from collections.abc import AsyncGenerator

from backend_common.database.engine import create_engine, create_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
AsyncSessionLocal = create_session_factory(engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session with transaction management.

    Yields:
        An async SQLAlchemy session. Commits on success, rolls back on error.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
