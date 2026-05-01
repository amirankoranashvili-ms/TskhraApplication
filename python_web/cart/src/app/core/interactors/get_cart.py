"""Interactor for retrieving the user's cart with enriched product data.

Fetches current stock quantities from the catalog service to include
in the cart response alongside locally stored cart data.
"""

import asyncio
from uuid import UUID

from src.app.core.cart.service import CartService
from src.app.core.facades.catalog_facade import CatalogFacade
from src.app.core.schemas.responses import CartItemResponse, CartResponse


class GetCartInteractor:
    """Use case for retrieving the current user's shopping cart."""

    def __init__(
        self, cart_service: CartService, catalog_facade: CatalogFacade
    ) -> None:
        """Initialize the interactor.

        Args:
            cart_service: Service for cart domain operations.
            catalog_facade: Facade for product catalog queries.
        """
        self.cart_service = cart_service
        self.catalog_facade = catalog_facade

    async def execute(self, user_id: UUID) -> CartResponse:
        """Retrieve the user's cart with current product stock information.

        Args:
            user_id: The authenticated user's identifier.

        Returns:
            Full cart response including items, totals, and stock quantities.
        """
        cart = await self.cart_service.get_or_create_cart(user_id)
        total = self.cart_service.calculate_total(cart)

        products = await asyncio.gather(
            *(self.catalog_facade.get_product(item.product_id) for item in cart.items)
        )
        stock_map = {
            item.product_id: prod.get("stock_quantity")
            for item, prod in zip(cart.items, products)
            if prod
        }

        items = [
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                product_title=item.product_title,
                product_image_url=item.product_image_url,
                subtotal=item.unit_price * item.quantity,
                stock_quantity=stock_map.get(item.product_id),
            )
            for item in cart.items
        ]

        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=items,
            status=cart.status.value,
            total=total,
            created_at=cart.created_at,
            updated_at=cart.updated_at,
        )
