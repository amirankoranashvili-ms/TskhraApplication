"""Interactor for creating payment orders from internal service requests."""

from src.app.core.facades.order_facade import OrderFacade
from src.app.core.schemas.requests import CreateOrderRequest
from src.app.core.schemas.responses import CreateOrderResponse


class CreateOrderInternalInteractor:
    """Creates a payment order on behalf of an internal service (e.g. booking)."""

    def __init__(self, facade: OrderFacade) -> None:
        self.facade = facade

    async def execute(self, request: CreateOrderRequest) -> CreateOrderResponse:
        items = [
            {
                "entity_id": item.entity_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "product_title": item.product_title,
            }
            for item in request.items
        ]
        order = await self.facade.create_order_from_checkout(
            user_id=request.user_id,
            items=items,
            total_amount=request.total_amount,
        )
        return CreateOrderResponse(order_id=order.id)
