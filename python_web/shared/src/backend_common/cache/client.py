"""Redis client factory.

Provides a single function for creating an async Redis client from a URL,
with string decoding enabled by default.
"""

import redis.asyncio as redis


def create_redis_client(url: str) -> redis.Redis:
    """Create an async Redis client from a connection URL.

    Args:
        url: Redis connection URL (e.g. ``redis://localhost:6379/0``).

    Returns:
        An async Redis client with ``decode_responses`` enabled.
    """
    return redis.from_url(url, decode_responses=True)