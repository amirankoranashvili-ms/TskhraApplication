"""Database session dependency with automatic commit/rollback.

Provides an async generator suitable for use as a FastAPI dependency
that manages the session lifecycle within a request.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session that commits on success or rolls back on error.

    Intended for use as a FastAPI dependency via ``functools.partial``.

    Args:
        session_factory: The async session factory to create sessions from.

    Yields:
        An active ``AsyncSession`` that is automatically committed when the
        request completes, or rolled back if an exception occurs.
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise