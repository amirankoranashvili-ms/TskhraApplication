"""RabbitMQ connection lifecycle management.

Maintains a module-level singleton connection with automatic reconnection
support via aio_pika's robust connection mechanism.
"""

import aio_pika
from aio_pika.abc import AbstractRobustConnection


_connection: AbstractRobustConnection | None = None


async def get_rabbitmq_connection(url: str) -> AbstractRobustConnection:
    """Get or create a robust RabbitMQ connection.

    Reuses an existing connection if it is still open, otherwise
    establishes a new one with automatic reconnection support.

    Args:
        url: The AMQP connection URL (e.g. ``amqp://guest:guest@localhost/``).

    Returns:
        A robust async RabbitMQ connection.
    """
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(url)
    return _connection


async def close_rabbitmq_connection() -> None:
    """Close the global RabbitMQ connection if it is open."""
    global _connection
    if _connection and not _connection.is_closed:
        await _connection.close()
        _connection = None