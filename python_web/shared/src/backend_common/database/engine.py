"""Async SQLAlchemy engine and session factory creation.

Provides factory functions with sensible defaults for connection pooling,
pre-ping health checks, and asyncpg compatibility settings.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def create_engine(database_url: str, **kwargs) -> AsyncEngine:
    """Create an async SQLAlchemy engine with production-ready defaults.

    Args:
        database_url: The async database URL (e.g. ``postgresql+asyncpg://...``).
        **kwargs: Override defaults such as ``echo``, ``pool_size``, or
            ``max_overflow``. Additional kwargs are passed through to
            ``create_async_engine``.

    Returns:
        A configured async SQLAlchemy engine.
    """
    return create_async_engine(
        database_url,
        echo=kwargs.pop("echo", False),
        pool_size=kwargs.pop("pool_size", 20),
        max_overflow=kwargs.pop("max_overflow", 10),
        pool_pre_ping=True,
        connect_args={"prepared_statement_cache_size": 0},
        **kwargs,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine.

    Args:
        engine: The async SQLAlchemy engine to bind sessions to.

    Returns:
        A session factory that produces ``AsyncSession`` instances with
        ``expire_on_commit`` disabled.
    """
    return async_sessionmaker(engine, expire_on_commit=False)