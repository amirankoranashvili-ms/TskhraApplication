"""Async Neo4j driver factory.

Provides a factory function to create an async Neo4j driver, following
the same pattern as ``cache.client.create_redis_client``.
"""

from neo4j import AsyncGraphDatabase, AsyncDriver


def create_neo4j_driver(
    uri: str,
    user: str,
    password: str,
    max_connection_pool_size: int = 50,
) -> AsyncDriver:
    """Create an async Neo4j driver instance.

    Args:
        uri: Neo4j connection URI (e.g. ``bolt://localhost:7687``).
        user: Neo4j username.
        password: Neo4j password.
        max_connection_pool_size: Maximum number of connections in the pool.

    Returns:
        An ``AsyncDriver`` instance ready for session creation.
    """
    return AsyncGraphDatabase.driver(
        uri,
        auth=(user, password),
        max_connection_pool_size=max_connection_pool_size,
    )
