"""Interactor for updating the quantity of a cart item.

Validates product stock availability before applying the quantity change.
"""

from uuid import UUID

from src.app.core.cart.exceptions import (
    CartItemNotFoundException,
    ProductNotAvailableException,
)
from src.app.core.cart.service import CartService
from src.app.core.facades.catalog_facade import CatalogFacade
from src.app.core.schemas.requests import UpdateCartItemRequest
from src.app.core.schemas.responses import CartItemResponse


class UpdateCartItemInteractor:
    """Use case for updating a cart item's quantity."""

    def __init__(
        self,
        cart_service: CartService,
        catalog_facade: CatalogFacade,
    ) -> None:
        """Initialize the interactor.

        Args:
            cart_service: Service for cart domain operations.
            catalog_facade: Facade for product catalog queries.
        """
        self.cart_service = cart_service
        self.catalog_facade = catalog_facade

    async def execute(
        self, user_id: UUID, item_id: UUID, request: UpdateCartItemRequest
    ) -> CartItemResponse:
        """Update the quantity of a cart item after verifying stock availability.

        Args:
            user_id: The authenticated user's identifier.
            item_id: The identifier of the cart item to update.
            request: Request payload containing the new quantity.

        Returns:
            Response with the updated cart item details.

        Raises:
            CartItemNotFoundException: If the item is not in the cart.
            ProductNotAvailableException: If the product has insufficient stock.
        """
        cart = await self.cart_service.get_or_create_cart(user_id)

        item = None
        for cart_item in cart.items:
            if cart_item.id == item_id:
                item = cart_item
                break

        if item is None:
            raise CartItemNotFoundException()

        available = await self.catalog_facade.validate_product_available(
            item.product_id, request.quantity
        )
        if not available:
            raise ProductNotAvailableException()

        updated = await self.cart_service.update_quantity(
            cart, item_id, request.quantity
        )

        return CartItemResponse(
            id=updated.id,
            product_id=updated.product_id,
            quantity=updated.quantity,
            unit_price=updated.unit_price,
            product_title=updated.product_title,
            product_image_url=updated.product_image_url,
            subtotal=updated.unit_price * updated.quantity,
        )
