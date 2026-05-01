import json

from aiokafka import AIOKafkaProducer


class KafkaEventPublisher:
    def __init__(
        self,
        producer: AIOKafkaProducer,
        default_topic: str = "payment-events",
    ) -> None:
        self.producer = producer
        self.default_topic = default_topic

    async def publish(self, routing_key: str, payload: dict) -> None:
        await self.producer.send_and_wait(
            self.default_topic,
            value=payload,
            key=routing_key.encode(),
        )
