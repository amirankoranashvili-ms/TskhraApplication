"""Internal API router for service-to-service communication.

Not exposed through the public API gateway — internal network only.
"""

from fastapi import APIRouter

from src.app.core.schemas.requests import CreateOrderRequest
from src.app.core.schemas.responses import CreateOrderResponse
from src.app.infra.web.dependables import CreateOrderDep

internal_router = APIRouter(prefix="/internal", include_in_schema=False)


@internal_router.post("/orders", status_code=201)
async def create_order(
    request: CreateOrderRequest,
    interactor: CreateOrderDep = None,
) -> CreateOrderResponse:
    """Create a payment order on behalf of an internal service.

    Used by booking service and other internal services to initiate
    a payment order without going through the cart checkout flow.

    Args:
        request: Order details including user_id, items, and total_amount.
        interactor: Injected order creation interactor.

    Returns:
        The created order_id for use in the payment flow.
    """
    return await interactor.execute(request)
