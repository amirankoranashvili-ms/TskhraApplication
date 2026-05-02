"""FastAPI router defining the cart REST API endpoints.

Exposes endpoints for viewing, modifying, and checking out the
authenticated user's shopping cart.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from backend_common.error_handlers import merge_responses
from backend_common.schemas import MessageResponse

from src.app.core.schemas.requests import AddToCartRequest, UpdateCartItemRequest
from src.app.core.schemas.responses import (
    CartItemResponse,
    CartResponse,
    CheckoutResponse,
)
from src.app.infra.auth.auth import get_current_user_id
from src.app.infra.web.dependables import (
    AddToCartDep,
    CheckoutDep,
    ClearCartDep,
    GetCartDep,
    RemoveFromCartDep,
    UpdateCartItemDep,
)
from src.app.infra.web.handler import (
    CartCheckedOutResponse,
    CartEmptyResponse,
    CartItemNotFoundResponse,
    ExternalServiceResponse,
    ProductNotAvailableResponse,
)

cart_router = APIRouter(tags=["Cart"])


@cart_router.get("/")
async def get_my_cart(
    interactor: GetCartDep,
    user_id: UUID = Depends(get_current_user_id),
) -> CartResponse:
    """Retrieve the authenticated user's shopping cart.

    Args:
        interactor: Injected use-case for fetching the cart.
        user_id: The authenticated user's identifier.

    Returns:
        The user's cart with items and totals.
    """
    return await interactor.execute(user_id)


@cart_router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    responses=merge_responses(
        ProductNotAvailableResponse,
        ExternalServiceResponse,
        CartCheckedOutResponse,
    ),
)
async def add_item_to_cart(
    request: AddToCartRequest,
    interactor: AddToCartDep,
    user_id: UUID = Depends(get_current_user_id),
) -> CartItemResponse:
    """Add a product to the authenticated user's cart.

    Args:
        request: Payload containing product_id and quantity.
        interactor: Injected use-case for adding items.
        user_id: The authenticated user's identifier.

    Returns:
        The created or updated cart item details.
    """
    return await interactor.execute(user_id, request)


@cart_router.put(
    "/items/{item_id}",
    responses=merge_responses(
        CartItemNotFoundResponse,
        ProductNotAvailableResponse,
        CartCheckedOutResponse,
    ),
)
async def update_cart_item(
    item_id: UUID,
    request: UpdateCartItemRequest,
    interactor: UpdateCartItemDep,
    user_id: UUID = Depends(get_current_user_id),
) -> CartItemResponse:
    """Update the quantity of an item in the user's cart.

    Args:
        item_id: The cart item to update.
        request: Payload containing the new quantity.
        interactor: Injected use-case for updating items.
        user_id: The authenticated user's identifier.

    Returns:
        The updated cart item details.
    """
    return await interactor.execute(user_id, item_id, request)


@cart_router.delete(
    "/items",
    responses=merge_responses(CartCheckedOutResponse),
)
async def clear_cart(
    interactor: ClearCartDep,
    user_id: UUID = Depends(get_current_user_id),
) -> MessageResponse:
    """Remove all items from the authenticated user's cart.

    Args:
        interactor: Injected use-case for clearing the cart.
        user_id: The authenticated user's identifier.

    Returns:
        A confirmation message.
    """
    return await interactor.execute(user_id)


@cart_router.delete(
    "/items/{item_id}",
    responses=merge_responses(CartItemNotFoundResponse, CartCheckedOutResponse),
)
async def remove_cart_item(
    item_id: UUID,
    interactor: RemoveFromCartDep,
    user_id: UUID = Depends(get_current_user_id),
) -> MessageResponse:
    """Remove an item from the user's cart.

    Args:
        item_id: The cart item to remove.
        interactor: Injected use-case for removing items.
        user_id: The authenticated user's identifier.

    Returns:
        A confirmation message.
    """
    return await interactor.execute(user_id, item_id)


@cart_router.post(
    "/checkout",
    responses=merge_responses(CartEmptyResponse, CartCheckedOutResponse),
)
async def checkout_cart(
    interactor: CheckoutDep,
    user_id: UUID = Depends(get_current_user_id),
) -> CheckoutResponse:
    """Process checkout for the user's cart.

    Args:
        interactor: Injected use-case for checkout.
        user_id: The authenticated user's identifier.

    Returns:
        Checkout confirmation with cart ID, status, and total.
    """
    return await interactor.execute(user_id)
