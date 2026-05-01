import logging

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from src.app.core.config import settings

logger = logging.getLogger(__name__)

producer: AIOKafkaProducer | None = None


async def init_kafka_producer() -> AIOKafkaProducer:
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: __import__("json").dumps(v).encode(),
    )
    await producer.start()
    logger.info("Kafka producer started.")
    return producer


async def create_kafka_consumer(*topics: str) -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        value_deserializer=lambda v: __import__("json").loads(v),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    await consumer.start()
    logger.info("Kafka consumer started for topics: %s", topics)
    return consumer


async def close_kafka_producer() -> None:
    global producer
    if producer:
        await producer.stop()
        producer = None
        logger.info("Kafka producer stopped.")
