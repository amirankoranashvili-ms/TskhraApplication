import logging

logger = logging.getLogger(__name__)

REPLY_TOPIC = "product-replies"


class ProviderReplyPublisher:
    @classmethod
    async def send_reply(cls, status: str, payload: dict, action: str = "upload"):
        from src.app.infra.broker.connection import producer

        if not producer:
            logger.error("Cannot publish message: Kafka producer is not initialized.")
            return

        key = f"product.{action}.{status.lower()}"
        payload["event_type"] = key
        await producer.send_and_wait(REPLY_TOPIC, value=payload, key=key.encode())
        logger.info("Published reply event '%s' to Kafka topic '%s'.", key, REPLY_TOPIC)
