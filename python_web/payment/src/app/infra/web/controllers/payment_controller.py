"""Payment API router.

Thin controller layer that delegates to interactors and facades for business logic.
"""

import json
import logging
from uuid import UUID

from backend_common.error_handlers import merge_responses
from backend_common.schemas import MessageResponse
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.app.core.schemas.requests import WebhookPayload, validate_redirect_uri
from src.app.core.schemas.responses import (
    OrderItemResponse,
    OrderPaginatedResponse,
    OrderResponse,
    OrderWithPaymentResponse,
)
from src.app.infra.auth.auth import get_current_user_id
from src.app.infra.web.dependables import (
    OrderHistoryDep,
    OrderServiceDep,
    ProcessPaymentDep,
    VerifyPaymentDep,
    WebhookDep,
    _get_payment_gateway,
)
from src.app.infra.web.handler import (
    OrderAccessDeniedResponse,
    OrderNotFoundResponse,
    OrderNotPayableResponse,
    PaymentFailedResponse,
)

logger = logging.getLogger(__name__)

payment_router = APIRouter(tags=["Payment"])


@payment_router.get("/")
async def get_order_history(
    user_id: UUID = Depends(get_current_user_id),
    interactor: OrderHistoryDep = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> OrderPaginatedResponse:
    """Retrieve paginated order history for the authenticated user.

    Args:
        user_id: UUID extracted from the JWT token.
        interactor: Injected order history interactor.
        page: Page number (1-based).
        limit: Maximum orders per page (1-100).

    Returns:
        Paginated list of orders with metadata.
    """
    return await interactor.execute(user_id, page, limit)


@payment_router.get(
    "/{order_id}",
    responses=merge_responses(OrderNotFoundResponse, OrderAccessDeniedResponse),
)
async def get_order_details(
    order_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: OrderServiceDep = None,
) -> OrderResponse:
    """Retrieve details for a specific order.

    Args:
        order_id: UUID of the order to retrieve.
        user_id: UUID extracted from the JWT token.
        service: Injected order service.

    Returns:
        The order details including line items.

    Raises:
        EntityNotFoundException: If the order does not exist.
        AccessDeniedException: If the user does not own the order.
    """
    order = await service.get_order(order_id, user_id)
    return OrderResponse(
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
    )


@payment_router.post(
    "/{order_id}/pay",
    responses=merge_responses(
        OrderNotFoundResponse,
        OrderAccessDeniedResponse,
        OrderNotPayableResponse,
        PaymentFailedResponse,
    ),
)
async def process_payment(
    order_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    interactor: ProcessPaymentDep = None,
    success_redirect_uri: str | None = Query(default=None),
    fail_redirect_uri: str | None = Query(default=None),
) -> OrderWithPaymentResponse:
    """Process a payment for the specified order.

    Args:
        order_id: UUID of the order to pay for.
        user_id: UUID extracted from the JWT token.
        interactor: Injected payment processing interactor.
        success_redirect_uri: URL to redirect after successful payment.
        fail_redirect_uri: URL to redirect after failed payment.

    Returns:
        The updated order with payment details.

    Raises:
        PaymentFailedException: If the payment is declined.
    """
    try:
        success_redirect_uri = validate_redirect_uri(success_redirect_uri)
        fail_redirect_uri = validate_redirect_uri(fail_redirect_uri)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return await interactor.execute(
        order_id, user_id, success_redirect_uri, fail_redirect_uri
    )


@payment_router.post(
    "/{order_id}/verify",
    responses=merge_responses(OrderNotFoundResponse, OrderAccessDeniedResponse),
)
async def verify_payment(
    order_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    interactor: VerifyPaymentDep = None,
) -> OrderWithPaymentResponse:
    """Verify payment status with the provider and update order if confirmed.

    Call this after the customer returns from the KeepZ payment page.

    Args:
        order_id: UUID of the order to verify.
        user_id: UUID extracted from the JWT token.
        interactor: Injected verify payment interactor.

    Returns:
        The updated order with current payment status.
    """
    return await interactor.execute(order_id, user_id)


@payment_router.post("/webhooks/payment")
async def payment_webhook(
    request: Request,
    interactor: WebhookDep = None,
) -> MessageResponse:

    body = await request.body()
    logger.info("KeepZ webhook raw body: %s", body.decode())
    try:
        data = json.loads(body)
        if "encryptedData" in data and "encryptedKeys" in data:
            gateway = _get_payment_gateway()
            if hasattr(gateway, "_decrypt_response"):
                data = gateway._decrypt_response(
                    data["encryptedData"], data["encryptedKeys"]
                )
                logger.info("KeepZ webhook decrypted: %s", data)
        payload = WebhookPayload.model_validate(data)
    except Exception as exc:
        logger.error("KeepZ webhook parse error: %s | body: %s", exc, body.decode())
        return MessageResponse(message="Webhook received, parse error.")
    return await interactor.execute(payload)
