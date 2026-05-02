import asyncio
import json
import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer

from src.app.core.facades.order_facade import OrderFacade
from src.app.core.interactors.create_order import CreateOrderInteractor
from src.app.core.order.entities import OrderStatus
from src.app.core.order.service import OrderService
from src.app.core.payment.service import PaymentService
from src.app.infra.broker.publisher import KafkaEventPublisher
from src.app.infra.database.config import session_factory
from src.app.infra.database.repositories import (
    SqlAlchemyOrderRepository,
    SqlAlchemyPaymentRepository,
)

logger = logging.getLogger(__name__)

VENDOR_TO_ORDER_STATUS = {
    "SHIPPED": OrderStatus.SHIPPED,
    "DELIVERED": OrderStatus.DELIVERED,
}


class CheckoutEventConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        publisher: KafkaEventPublisher,
        payment_gateway,
        cache_service,
    ) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.publisher = publisher
        self.payment_gateway = payment_gateway
        self.cache_service = cache_service
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            "cart-events",
            bootstrap_servers=self.bootstrap_servers,
            group_id="payment-checkout",
            value_deserializer=lambda v: json.loads(v),
            key_deserializer=lambda k: k.decode() if k else None,
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume())

    async def _consume(self) -> None:
        try:
            async for msg in self._consumer:
                if msg.key != "cart.checkout":
                    continue
                logger.info("Received cart.checkout event: %s", msg.value.get("cart_id"))
                await self._handle(msg.value)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("CheckoutEventConsumer crashed")

    async def _handle(self, payload: dict) -> None:
        async with session_factory() as session:
            try:
                order_repo = SqlAlchemyOrderRepository(session)
                payment_repo = SqlAlchemyPaymentRepository(session)
                order_service = OrderService(order_repository=order_repo)
                payment_service = PaymentService(
                    payment_repository=payment_repo,
                    payment_gateway=self.payment_gateway,
                    cache=self.cache_service,
                )
                facade = OrderFacade(
                    order_service=order_service,
                    payment_service=payment_service,
                    publisher=self.publisher,
                )
                interactor = CreateOrderInteractor(facade=facade)
                await interactor.execute(payload)
                await session.commit()
                logger.info("Order created from checkout event")
            except Exception:
                await session.rollback()
                logger.exception("Failed to process checkout event")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            await self._consumer.stop()


class VendorStatusConsumer:
    def __init__(self, bootstrap_servers: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            "vendor-events",
            bootstrap_servers=self.bootstrap_servers,
            group_id="payment-vendor-status",
            value_deserializer=lambda v: json.loads(v),
            key_deserializer=lambda k: k.decode() if k else None,
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume())

    async def _consume(self) -> None:
        try:
            async for msg in self._consumer:
                if msg.key != "vendor.order.status_updated":
                    continue
                await self._handle(msg.value)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("VendorStatusConsumer crashed")

    async def _handle(self, payload: dict) -> None:
        order_id = UUID(payload["order_id"])
        vendor_status = payload["status"]

        new_status = VENDOR_TO_ORDER_STATUS.get(vendor_status)
        if not new_status:
            logger.info("Ignoring vendor status %s for order %s", vendor_status, order_id)
            return

        async with session_factory() as session:
            try:
                order_repo = SqlAlchemyOrderRepository(session)
                order_service = OrderService(order_repository=order_repo)
                await order_service.update_order_status(order_id, new_status)
                await session.commit()
                logger.info(
                    "Order %s status updated to %s from vendor event",
                    order_id,
                    new_status.value,
                )
            except Exception:
                await session.rollback()
                logger.exception("Failed to process vendor status event for order %s", order_id)

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            await self._consumer.stop()
