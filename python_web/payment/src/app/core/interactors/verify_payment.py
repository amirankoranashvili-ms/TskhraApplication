"""Interactor for verifying payment status with the payment provider."""

from uuid import UUID

from src.app.core.facades.order_facade import OrderFacade
from src.app.core.schemas.responses import (
    OrderItemResponse,
    OrderWithPaymentResponse,
    PaymentResponse,
)


class VerifyPaymentInteractor:
    """Checks payment status at the gateway and updates order if confirmed."""

    def __init__(self, facade: OrderFacade) -> None:
        self.facade = facade

    async def execute(self, order_id: UUID, user_id: UUID) -> OrderWithPaymentResponse:
        order, _ = await self.facade.verify_payment(order_id, user_id)

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
                redirect_url=None,
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
