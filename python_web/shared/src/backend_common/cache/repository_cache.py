"""Read-through cache layer for repository data access.

Provides get-or-set semantics with custom serialization, pattern-based
invalidation, and support for both single items and lists.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

import redis.asyncio as redis

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RepositoryCache:
    """Redis-backed read-through cache with serialization support.

    Wraps a Redis client to provide cache-aside pattern with configurable
    key prefixes, TTLs, and pluggable serialization/deserialization.

    Attributes:
        client: The async Redis client.
        prefix: Key namespace prefix to avoid collisions.
        ttl: Default time-to-live in seconds for cached entries.
    """

    def __init__(
        self,
        client: redis.Redis,
        prefix: str = "cache",
        ttl: int = 300,
    ) -> None:
        """Initialize the repository cache.

        Args:
            client: An async Redis client instance.
            prefix: Key prefix for namespacing cache entries.
            ttl: Default TTL in seconds for cached values.
        """
        self.client = client
        self.prefix = prefix
        self.ttl = ttl

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get_or_set(
        self,
        key: str,
        loader: Callable[[], Awaitable[T | None]],
        serializer: Callable[[T], str],
        deserializer: Callable[[str], T],
        ttl: int | None = None,
    ) -> T | None:
        """Return a cached value or load, cache, and return it.

        Args:
            key: The cache key (without prefix).
            loader: Async callable that fetches the value on cache miss.
            serializer: Converts the value to a string for storage.
            deserializer: Converts the cached string back to the value type.
            ttl: Optional TTL override in seconds.

        Returns:
            The cached or freshly loaded value, or None if the loader returns None.
        """
        full_key = self._key(key)
        cached = await self.client.get(full_key)

        if cached is not None:
            logger.debug("Cache HIT: %s", full_key)
            return deserializer(cached)

        logger.debug("Cache MISS: %s", full_key)
        value = await loader()

        if value is not None:
            serialized = serializer(value)
            await self.client.setex(full_key, ttl or self.ttl, serialized)

        return value

    async def get(self, key: str, deserializer: Callable[[str], T]) -> T | None:
        """Retrieve a cached value without loading on miss.

        Args:
            key: The cache key (without prefix).
            deserializer: Converts the cached string back to the value type.

        Returns:
            The deserialized value, or None if not cached.
        """
        cached = await self.client.get(self._key(key))
        if cached is not None:
            return deserializer(cached)
        return None

    async def set(
        self,
        key: str,
        value: T,
        serializer: Callable[[T], str],
        ttl: int | None = None,
    ) -> None:
        """Store a value in the cache.

        Args:
            key: The cache key (without prefix).
            value: The value to cache.
            serializer: Converts the value to a string for storage.
            ttl: Optional TTL override in seconds.
        """
        await self.client.setex(self._key(key), ttl or self.ttl, serializer(value))

    async def invalidate(self, key: str) -> None:
        """Remove a single entry from the cache.

        Args:
            key: The cache key (without prefix) to invalidate.
        """
        full_key = self._key(key)
        deleted = await self.client.delete(full_key)
        if deleted:
            logger.debug("Cache INVALIDATED: %s", full_key)

    async def invalidate_pattern(self, pattern: str) -> None:
        """Remove all cache entries matching a glob pattern.

        Uses Redis SCAN to iterate keys without blocking the server.

        Args:
            pattern: A glob-style pattern (without prefix) to match keys against.
        """
        full_pattern = self._key(pattern)
        cursor = 0
        deleted_count = 0
        while True:
            cursor, keys = await self.client.scan(cursor, match=full_pattern, count=100)
            if keys:
                await self.client.delete(*keys)
                deleted_count += len(keys)
            if cursor == 0:
                break
        if deleted_count:
            logger.debug("Cache INVALIDATED %d keys matching: %s", deleted_count, full_pattern)

    async def get_or_set_list(
        self,
        key: str,
        loader: Callable[[], Awaitable[list[T]]],
        serializer: Callable[[list[T]], str],
        deserializer: Callable[[str], list[T]],
        ttl: int | None = None,
    ) -> list[T]:
        """Return a cached list or load, cache, and return it.

        Args:
            key: The cache key (without prefix).
            loader: Async callable that fetches the list on cache miss.
            serializer: Converts the list to a string for storage.
            deserializer: Converts the cached string back to a list.
            ttl: Optional TTL override in seconds.

        Returns:
            The cached or freshly loaded list of items.
        """
        full_key = self._key(key)
        cached = await self.client.get(full_key)

        if cached is not None:
            logger.debug("Cache HIT (list): %s", full_key)
            return deserializer(cached)

        logger.debug("Cache MISS (list): %s", full_key)
        values = await loader()

        if values:
            serialized = serializer(values)
            await self.client.setex(full_key, ttl or self.ttl, serialized)

        return values