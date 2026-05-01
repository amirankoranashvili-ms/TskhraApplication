"""Interactor for initiating a swap order with 0 GEL card-save payment."""

from src.app.core.facades.order_facade import OrderFacade
from src.app.core.schemas.requests import CreateSwapOrderRequest
from src.app.core.schemas.responses import SwapOrderResponse


class CreateSwapOrderInteractor:
    def __init__(self, facade: OrderFacade) -> None:
        self.facade = facade

    async def execute(self, request: CreateSwapOrderRequest) -> SwapOrderResponse:
        order, payment_url = await self.facade.create_swap_order(
            user_id=request.participant.user_id,
            swap_id=request.swap_id,
            commission_amount=request.participant.commission_amount,
            success_redirect_uri=request.success_redirect_uri,
            fail_redirect_uri=request.fail_redirect_uri,
        )
        return SwapOrderResponse(order_id=order.id, payment_url=payment_url)