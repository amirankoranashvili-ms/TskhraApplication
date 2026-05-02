"""Arq worker Redis configuration utilities.

Provides a helper to parse a Redis URL into ``RedisSettings`` for use
with the arq task queue worker.
"""

from arq.connections import RedisSettings


def get_redis_settings(redis_url: str) -> RedisSettings:
    """Parse a Redis URL into arq ``RedisSettings``.

    Args:
        redis_url: A Redis connection URL (e.g. ``redis://localhost:6379/0``).

    Returns:
        An ``arq.connections.RedisSettings`` instance configured from the URL.
    """
    from urllib.parse import urlparse

    parsed = urlparse(redis_url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or "0"),
    )