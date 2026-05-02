"""Dead letter queue support for resilient message consumption.

Provides a consumer that retries failed messages up to a configurable limit,
then routes them to a dead letter queue, along with tooling for inspecting
and reprocessing dead-lettered messages.
"""

import json
import logging
from abc import ABC, abstractmethod

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

logger = logging.getLogger(__name__)


class ResilientConsumer(ABC):
    """Abstract message consumer with automatic retry and dead letter support.

    Failed messages are retried up to ``max_retries`` times before being
    routed to a dead letter queue for later inspection or reprocessing.

    Attributes:
        connection: The RabbitMQ connection.
        exchange_name: The topic exchange to consume from.
        queue_name: The main queue name.
        max_retries: Maximum retry attempts before dead-lettering.
        dlq_name: The dead letter queue name (derived from queue_name).
    """

    def __init__(
        self,
        connection: AbstractRobustConnection,
        exchange_name: str = "catalog_events",
        queue_name: str = "",
        max_retries: int = 3,
    ) -> None:
        """Initialize the resilient consumer.

        Args:
            connection: An active RabbitMQ connection.
            exchange_name: The topic exchange name.
            queue_name: The main queue name.
            max_retries: Maximum retries before dead-lettering a message.
        """
        self.connection = connection
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.dlq_name = f"{queue_name}.dlq"

    @abstractmethod
    def get_routing_keys(self) -> list[str]:
        """Return the list of routing key patterns to bind to.

        Returns:
            Routing key strings (may include wildcards).
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
        """Start consuming messages with retry and dead letter handling.

        Sets up the main queue, dead letter exchange, and dead letter queue,
        then begins asynchronous message consumption.
        """
        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        dlx_name = f"{self.exchange_name}.dlx"
        dlx = await channel.declare_exchange(
            dlx_name,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        dlq = await channel.declare_queue(self.dlq_name, durable=True)
        await dlq.bind(dlx, routing_key=self.queue_name)

        main_queue = await channel.declare_queue(
            self.queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": dlx_name,
                "x-dead-letter-routing-key": self.queue_name,
            },
        )

        for key in self.get_routing_keys():
            await main_queue.bind(exchange, routing_key=key)

        async def on_message(message: AbstractIncomingMessage) -> None:
            retry_count = (message.headers or {}).get("x-retry-count", 0)

            try:
                payload = json.loads(message.body)
                await self.handle_message(message.routing_key, payload)
                await message.ack()
            except Exception as e:
                if retry_count < self.max_retries:
                    logger.warning(
                        "Retry %d/%d for message on %s: %s",
                        retry_count + 1, self.max_retries, message.routing_key, e,
                    )
                    await message.nack(requeue=False)

                    retry_message = aio_pika.Message(
                        body=message.body,
                        content_type="application/json",
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        headers={"x-retry-count": retry_count + 1},
                    )
                    await exchange.publish(retry_message, routing_key=message.routing_key)
                else:
                    logger.error(
                        "Message DEAD LETTERED after %d retries on %s: %s",
                        self.max_retries, message.routing_key, e,
                    )
                    await message.nack(requeue=False)

        await main_queue.consume(on_message)
        logger.info(
            "Resilient consumer started: queue=%s, dlq=%s, max_retries=%d",
            self.queue_name, self.dlq_name, self.max_retries,
        )


class DLQInspector:
    """Utility for inspecting and reprocessing dead letter queue messages.

    Attributes:
        connection: The RabbitMQ connection.
    """

    def __init__(self, connection: AbstractRobustConnection) -> None:
        """Initialize the DLQ inspector.

        Args:
            connection: An active RabbitMQ connection.
        """
        self.connection = connection

    async def get_dlq_messages(self, dlq_name: str, limit: int = 100) -> list[dict]:
        """Peek at messages in a dead letter queue without consuming them.

        Messages are nacked with requeue so they remain in the queue.

        Args:
            dlq_name: The dead letter queue name.
            limit: Maximum number of messages to retrieve.

        Returns:
            A list of dicts containing routing_key, body, headers, and timestamp.
        """
        channel = await self.connection.channel()
        queue = await channel.declare_queue(dlq_name, durable=True, passive=True)

        messages = []
        for _ in range(limit):
            message = await queue.get(no_ack=False, fail=False)
            if message is None:
                break
            messages.append({
                "routing_key": message.routing_key,
                "body": json.loads(message.body),
                "headers": dict(message.headers or {}),
                "timestamp": str(message.timestamp),
            })
            await message.nack(requeue=True)
        return messages

    async def reprocess_message(
        self,
        dlq_name: str,
        exchange_name: str,
    ) -> int:
        """Move all messages from a DLQ back to the main exchange for reprocessing.

        Each message is republished with a reset retry count and then
        acknowledged from the DLQ.

        Args:
            dlq_name: The dead letter queue to drain.
            exchange_name: The exchange to republish messages to.

        Returns:
            The number of messages reprocessed.
        """
        channel = await self.connection.channel()
        queue = await channel.declare_queue(dlq_name, durable=True, passive=True)
        exchange = await channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True,
        )

        count = 0
        while True:
            message = await queue.get(no_ack=False, fail=False)
            if message is None:
                break
            new_msg = aio_pika.Message(
                body=message.body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers={"x-retry-count": 0},
            )
            await exchange.publish(new_msg, routing_key=message.routing_key)
            await message.ack()
            count += 1

        logger.info("Reprocessed %d messages from %s", count, dlq_name)
        return count