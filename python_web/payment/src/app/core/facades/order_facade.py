"""Facade orchestrating the order lifecycle.

Coordinates order creation, payment processing, refunds, and event
publishing (payment.completed, payment.failed, payment.refunded).
"""

import logging
from typing import Any
from uuid import UUID

from backend_common.broker.publisher import EventPublisher

from src.app.core.order.entities import Order, OrderStatus
from src.app.core.order.exceptions import (
    OrderAlreadyPaidException,
    OrderNotPayableException,
)
from src.app.core.order.service import OrderService
from src.app.core.payment.entities import PaymentStatus
from src.app.core.payment.exceptions import PaymentFailedException
from src.app.core.payment.service import PaymentService

logger = logging.getLogger(__name__)


class OrderFacade:
    """High-level facade that ties together order, payment, and event services."""

    def __init__(
        self,
        order_service: OrderService,
        payment_service: PaymentService,
        publisher: EventPublisher,
    ) -> None:
        """Initialize with order, payment, and event publishing services.

        Args:
            order_service: Service for order operations.
            payment_service: Service for payment operations.
            publisher: Event publisher for domain events.
        """
        self.order_service = order_service
        self.payment_service = payment_service
        self.publisher = publisher

    async def create_order_from_checkout(
        self,
        user_id: UUID,
        items: list[dict],
        total_amount: float,
    ) -> Order:
        """Create a new order from checkout data.

        Args:
            user_id: ID of the user placing the order.
            items: List of item dicts from the checkout cart.
            total_amount: Pre-calculated order total.

        Returns:
            The newly created Order entity.
        """
        order = await self.order_service.create_order_from_checkout(
            user_id=user_id,
            items=items,
            total_amount=total_amount,
        )
        logger.info("Order %s created for user %s", order.id, user_id)
        return order

    async def process_payment_for_order(
        self,
        order_id: UUID,
        user_id: UUID,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Order, str | None]:
        """Process payment for an order and publish the outcome event.

        Args:
            order_id: The order to pay for.
            user_id: The authenticated user (must own the order).
            metadata: Optional provider-specific metadata.

        Returns:
            The updated Order marked as PAID.

        Raises:
            PaymentFailedException: If the gateway declines the charge.
        """
        # 1. Get the order and verify access
        order = await self.order_service.get_order(order_id, user_id)

        if order.status == OrderStatus.PAID:
            raise OrderAlreadyPaidException()
        if order.status != OrderStatus.PENDING:
            raise OrderNotPayableException()

        try:
            # 2. Process payment
            payment, redirect_url = await self.payment_service.process_payment(
                order_id=order.id,
                amount=order.total_amount,
                metadata=metadata,
            )

            if payment.status == PaymentStatus.PENDING:
                # Redirect-based flow (e.g. KeepZ): customer hasn't paid yet.
                # Webhook will call mark_as_paid() when confirmed.
                logger.info("Payment pending redirect for order %s", order.id)
                return order, redirect_url

            # 3. Mark order as paid and publish event
            # Publish first — if it fails, payment was made but we don't update order status
            # This is safer than marking paid and failing to notify downstream services
            await self.publisher.publish(
                routing_key="payment.completed",
                payload={
                    "order_id": str(order.id),
                    "user_id": str(user_id),
                    "payment_id": str(payment.id),
                    "total_amount": float(order.total_amount),
                    "items": [
                        {
                            "entity_id": item.entity_id,
                            "quantity": item.quantity,
                            "unit_price": float(item.unit_price),
                            "product_title": item.product_title,
                        }
                        for item in order.items
                    ],
                },
            )
            updated_order = await self.order_service.mark_as_paid(order.id)
            logger.info("Payment completed for order %s", order.id)
            return updated_order, redirect_url

        except PaymentFailedException as e:
            await self.publisher.publish(
                routing_key="payment.failed",
                payload={
                    "order_id": str(order.id),
                    "user_id": str(user_id),
                    "error": str(e),
                },
            )
            logger.warning("Payment failed for order %s: %s", order.id, e)
            raise

    async def verify_payment(
        self, order_id: UUID, user_id: UUID
    ) -> tuple[Order, str | None]:
        """Verify payment status with the gateway and update order if completed.

        Args:
            order_id: The order to verify.
            user_id: The authenticated user (must own the order).

        Returns:
            Tuple of (updated Order, redirect_url if still pending).
        """
        order = await self.order_service.get_order(order_id, user_id)
        payment = await self.payment_service.verify_payment(order.id)

        if payment.status == PaymentStatus.COMPLETED:
            if order.status.value != "PAID":
                await self.publisher.publish(
                    routing_key="payment.completed",
                    payload={
                        "order_id": str(order.id),
                        "user_id": str(user_id),
                        "payment_id": str(payment.id),
                        "total_amount": float(order.total_amount),
                        "items": [
                            {
                                "entity_id": item.entity_id,
                                "quantity": item.quantity,
                                "unit_price": float(item.unit_price),
                                "product_title": item.product_title,
                            }
                            for item in order.items
                        ],
                    },
                )
                updated_order = await self.order_service.mark_as_paid(order.id)
                logger.info("Payment verified and order %s marked as paid", order.id)
                return updated_order, None

        return order, None
