"""Interactor for processing payments against existing orders."""

from uuid import UUID

from src.app.core.facades.order_facade import OrderFacade
from src.app.core.schemas.responses import (
    OrderItemResponse,
    OrderWithPaymentResponse,
    PaymentResponse,
)


class ProcessPaymentInteractor:
    """Orchestrates payment processing for a given order."""

    def __init__(self, facade: OrderFacade) -> None:
        """Initialize with the order facade.

        Args:
            facade: Facade coordinating order and payment operations.
        """
        self.facade = facade

    async def execute(
        self,
        order_id: UUID,
        user_id: UUID,
        success_redirect_uri: str | None = None,
        fail_redirect_uri: str | None = None,
    ) -> OrderWithPaymentResponse:
        """Process a payment and return the order with payment details.

        Args:
            order_id: UUID of the order to pay for.
            user_id: UUID of the authenticated user.
            request: Payment request containing method and optional card info.
            success_redirect_uri: Validated redirect URI on payment success.
            fail_redirect_uri: Validated redirect URI on payment failure.

        Returns:
            Response combining the updated order and its payment details.

        Raises:
            PaymentFailedException: If the gateway declines the charge.
        """
        metadata = {}
        if success_redirect_uri:
            metadata["successRedirectUri"] = success_redirect_uri
        if fail_redirect_uri:
            metadata["failRedirectUri"] = fail_redirect_uri

        order, redirect_url = await self.facade.process_payment_for_order(
            order_id=order_id,
            user_id=user_id,
            metadata=metadata,
        )
        # Fetch payment info
        payment_service = self.facade.payment_service
        payment = await payment_service.get_payment_by_order(order.id)

        payment_resp = None
        if payment:
            payment_resp = PaymentResponse(
                id=payment.id,
                order_id=payment.order_id,
                amount=payment.amount,
                status=payment.status.value,
                provider_payment_id=payment.provider_payment_id,
                redirect_url=redirect_url,
                created_at=payment.created_at,
            )

        return OrderWithPaymentResponse(
            id=order.id,
            user_id=order.user_id,
            items=[
                OrderItemResponse(
                    id=item.id,
                    entity_id=item.entity_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    product_title=item.product_title,
                )
                for item in order.items
            ],
            status=order.status.value,
            total_amount=order.total_amount,
            created_at=order.created_at,
            updated_at=order.updated_at,
            payment=payment_resp,
        )
