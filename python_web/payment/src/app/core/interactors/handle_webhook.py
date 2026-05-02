"""Interactor for handling inbound payment provider webhooks."""

import logging

from backend_common.broker.publisher import EventPublisher
from backend_common.schemas import MessageResponse

from src.app.core.order.service import OrderService
from src.app.core.payment.entities import PaymentStatus
from src.app.core.payment.repository import IPaymentRepository
from src.app.core.schemas.requests import WebhookPayload

logger = logging.getLogger(__name__)


class HandleWebhookInteractor:
    """Processes payment provider webhook callbacks and updates internal state."""

    def __init__(
        self,
        order_service: OrderService,
        payment_repository: IPaymentRepository,
        publisher: EventPublisher,
    ) -> None:
        """Initialize with order service and payment repository.

        Args:
            order_service: Service for order status transitions.
            payment_repository: Repository for payment lookups and updates.
        """
        self.order_service = order_service
        self.payment_repository = payment_repository
        self.publisher = publisher

    async def execute(self, payload: WebhookPayload) -> MessageResponse:
        """Process a webhook payload and update payment/order status.

        Args:
            payload: The webhook payload from the payment provider.

        Returns:
            A MessageResponse indicating the processing result.
        """
        logger.info(
            "Webhook received: integratorOrderId=%s status=%s",
            payload.integratorOrderId,
            payload.status,
        )

        status_map = {
            "success": PaymentStatus.COMPLETED,
            "failed": PaymentStatus.FAILED,
        }

        internal_status = status_map.get(payload.status.lower())
        if not internal_status:
            logger.warning("Unknown webhook status: %s", payload.status)
            return MessageResponse(message="Webhook received, unknown status.")

        payment = await self.payment_repository.get_by_provider_id(
            payload.integratorOrderId
        )
        if not payment:
            logger.warning(
                "Payment not found for integratorOrderId=%s", payload.integratorOrderId
            )
            return MessageResponse(message="Payment not found.")

        await self.payment_repository.update_status(
            payment.id, internal_status, payload.integratorOrderId
        )

        if internal_status == PaymentStatus.COMPLETED:
            order = await self.order_service.mark_as_paid(payment.order_id)
            await self.publisher.publish(
                routing_key="payment.completed",
                payload={
                    "order_id": str(order.id),
                    "user_id": str(order.user_id),
                    "payment_id": str(payment.id),
                    "total_amount": float(order.total_amount),
                },
            )
            logger.info("Published payment.completed for order %s", order.id)
        elif internal_status == PaymentStatus.REFUNDED:
            await self.order_service.mark_as_refunded(payment.order_id)

        logger.info(
            "Webhook processed: integratorOrderId=%s -> %s",
            payload.integratorOrderId,
            internal_status.value,
        )

        return MessageResponse(message="Webhook processed successfully.")
