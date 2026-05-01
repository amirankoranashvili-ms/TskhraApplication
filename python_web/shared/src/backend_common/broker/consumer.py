"""Base message consumer for RabbitMQ topic exchanges.

Provides an abstract consumer that binds to routing keys, deserializes
incoming JSON messages, and delegates handling to subclass implementations.
"""

import json
import logging
from abc import ABC, abstractmethod

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

logger = logging.getLogger(__name__)


class BaseConsumer(ABC):
    """Abstract base class for RabbitMQ message consumers.

    Subclasses must implement ``get_routing_keys`` and ``handle_message``
    to define which events they subscribe to and how to process them.

    Attributes:
        connection: The RabbitMQ connection.
        exchange_name: The topic exchange to consume from.
        queue_name: The durable queue name for this consumer.
    """

    def __init__(
        self,
        connection: AbstractRobustConnection,
        exchange_name: str = "catalog_events",
        queue_name: str = "",
    ) -> None:
        """Initialize the consumer.

        Args:
            connection: An active RabbitMQ connection.
            exchange_name: The topic exchange name.
            queue_name: The queue name for this consumer.
        """
        self.connection = connection
        self.exchange_name = exchange_name
        self.queue_name = queue_name

    @abstractmethod
    def get_routing_keys(self) -> list[str]:
        """Return the list of routing key patterns to bind to.

        Returns:
            Routing key strings (may include wildcards like ``*.event``).
        """
        ...

    @abstractmethod
    async def handle_message(self, routing_key: str, payload: dict) -> None:
        """Process a single incoming message.

        Args:
            routing_key: The routing key the message was published with.
            payload: The deserialized JSON message body.
        """
        ...

    async def start(self) -> None:
        """Start consuming messages from the queue.

        Declares the exchange and queue, binds routing keys, and begins
        asynchronous message consumption.
        """
        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        queue = await channel.declare_queue(self.queue_name, durable=True)
        for key in self.get_routing_keys():
            await queue.bind(exchange, routing_key=key)

        async def on_message(message: AbstractIncomingMessage) -> None:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    await self.handle_message(message.routing_key, payload)
                except Exception:
                    logger.exception(
                        "Error processing message: routing_key=%s", message.routing_key
                    )

        await queue.consume(on_message)
        logger.info(
            "Consumer started: queue=%s, keys=%s", self.queue_name, self.get_routing_keys()
        )