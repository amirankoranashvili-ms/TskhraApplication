import json

from aiokafka import AIOKafkaProducer


class KafkaEventPublisher:
    def __init__(
        self,
        producer: AIOKafkaProducer,
        default_topic: str = "product-events",
    ) -> None:
        self.producer = producer
        self.default_topic = default_topic

    async def publish(self, routing_key: str, payload: dict) -> None:
        await self.producer.send_and_wait(
            self.default_topic,
            value=payload,
            key=routing_key.encode(),
        )


class ProductEventPublisher:
    def __init__(self, publisher: KafkaEventPublisher) -> None:
        self._publisher = publisher

    async def publish_product_created(self, product_data: dict) -> None:
        await self._publisher.publish("product.created", product_data)

    async def publish_product_updated(self, product_data: dict) -> None:
        await self._publisher.publish("product.updated", product_data)

    async def publish_product_deleted(self, product_id: int, supplier_id: int) -> None:
        await self._publisher.publish(
            "product.deleted", {"product_id": product_id, "supplier_id": supplier_id}
        )

    async def publish_seller_created(self, seller_data: dict) -> None:
        await self._publisher.publish("seller.created", seller_data)

    async def publish_seller_updated(self, seller_data: dict) -> None:
        await self._publisher.publish("seller.updated", seller_data)

    async def publish_order_status_updated(self, payload: dict) -> None:
        await self._publisher.publish("vendor.order.status_updated", payload)
