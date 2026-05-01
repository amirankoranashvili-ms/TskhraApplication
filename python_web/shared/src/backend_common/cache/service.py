"""High-level async cache service wrapping a Redis client.

Provides simple get/set/delete/exists operations with optional TTL support,
used as the primary caching abstraction throughout backend services.
"""

import redis.asyncio as redis


class CacheService:
    """Thin async wrapper around a Redis client for key-value caching.

    Attributes:
        client: The underlying async Redis client.
    """

    def __init__(self, client: redis.Redis) -> None:
        """Initialize the cache service.

        Args:
            client: An async Redis client instance.
        """
        self.client = client

    async def get(self, key: str) -> str | None:
        """Retrieve a value by key.

        Args:
            key: The cache key to look up.

        Returns:
            The cached string value, or None if the key does not exist.
        """
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Store a value with an optional time-to-live.

        Args:
            key: The cache key.
            value: The string value to store.
            ttl: Expiration time in seconds. If None, the key does not expire.
        """
        if ttl:
            await self.client.setex(key, ttl, value)
        else:
            await self.client.set(key, value)

    async def delete(self, key: str) -> None:
        """Remove a key from the cache.

        Args:
            key: The cache key to delete.
        """
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check whether a key exists in the cache.

        Args:
            key: The cache key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        return bool(await self.client.exists(key))

    async def increment(self, key: str) -> int:
        """Atomically increment an integer value.

        Args:
            key: The cache key to increment.

        Returns:
            The new value after incrementing.
        """
        return await self.client.incr(key)

    async def expire(self, key: str, ttl: int) -> None:
        """Set an expiration time on an existing key.

        Args:
            key: The cache key.
            ttl: Time-to-live in seconds.
        """
        await self.client.expire(key, ttl)