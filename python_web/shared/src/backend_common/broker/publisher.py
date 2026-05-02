"""Event publishing over RabbitMQ topic exchanges.

Provides a publisher that lazily initializes a channel and exchange,
then serializes and sends persistent JSON messages with routing keys.
"""

import json

import aio_pika
from aio_pika.abc import AbstractRobustConnection


class EventPublisher:
    """Publishes JSON events to a RabbitMQ topic exchange.

    Lazily creates the channel and declares the exchange on first publish.

    Attributes:
        connection: The RabbitMQ connection to use.
        exchange_name: The name of the topic exchange.
    """

    def __init__(self, connection: AbstractRobustConnection, exchange_name: str = "catalog_events") -> None:
        """Initialize the event publisher.

        Args:
            connection: An active RabbitMQ connection.
            exchange_name: The topic exchange name to publish to.
        """
        self.connection = connection
        self.exchange_name = exchange_name
        self._channel = None
        self._exchange = None

    async def _ensure_exchange(self) -> aio_pika.abc.AbstractExchange:
        if self._exchange is None:
            self._channel = await self.connection.channel()
            self._exchange = await self._channel.declare_exchange(
                self.exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
        return self._exchange

    async def publish(self, routing_key: str, payload: dict) -> None:
        """Publish a JSON message to the exchange.

        Args:
            routing_key: The topic routing key for the message.
            payload: The message body as a dictionary (serialized to JSON).
        """
        exchange = await self._ensure_exchange()
        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key=routing_key)

    async def close(self) -> None:
        """Close the publisher's channel if it is open."""
        if self._channel and not self._channel.is_closed:
            await self._channel.close()