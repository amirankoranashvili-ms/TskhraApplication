import json
import logging

from aiokafka import AIOKafkaProducer

from src.app.core.config import settings

logger = logging.getLogger(__name__)

producer: AIOKafkaProducer | None = None


async def init_kafka_producer() -> AIOKafkaProducer:
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await producer.start()
    logger.info("Kafka producer started.")
    return producer


async def close_kafka_producer() -> None:
    global producer
    if producer:
        await producer.stop()
        producer = None
        logger.info("Kafka producer stopped.")


class KafkaEventPublisher:
    def __init__(self, kafka_producer: AIOKafkaProducer, default_topic: str = "product-events") -> None:
        self.producer = kafka_producer
        self.default_topic = default_topic

    async def publish(self, routing_key: str, payload: dict) -> None:
        await self.producer.send_and_wait(
            self.default_topic,
            value=payload,
            key=routing_key.encode(),
        )
