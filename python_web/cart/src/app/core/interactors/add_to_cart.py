"""Interactor for adding a product to the user's cart.

Validates product availability through the catalog facade before
delegating to the cart service to persist the item.
"""

from uuid import UUID

from src.app.core.cart.exceptions import ProductNotAvailableException
from src.app.core.cart.service import CartService
from src.app.core.facades.catalog_facade import CatalogFacade
from src.app.core.schemas.requests import AddToCartRequest
from src.app.core.schemas.responses import CartItemResponse


class AddToCartInteractor:
    """Use case for adding a product to the shopping cart."""

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
        self, user_id: UUID, request: AddToCartRequest
    ) -> CartItemResponse:
        """Add a product to the user's cart.

        Args:
            user_id: The authenticated user's identifier.
            request: Request payload containing product_id and quantity.

        Returns:
            Response with the created or updated cart item details.

        Raises:
            ProductNotAvailableException: If the product is not found or out of stock.
        """
        product = await self.catalog_facade.get_product(request.product_id)
        if not product:
            raise ProductNotAvailableException("Product not found in catalog.")

        cart = await self.cart_service.get_or_create_cart(user_id)

        existing_item = await self.cart_service.get_item_by_product(
            cart.id, request.product_id
        )
        existing_quantity = existing_item.quantity if existing_item else 0

        total_quantity = existing_quantity + request.quantity
        stock = product.get("stock_quantity", 0)
        is_active = product.get("is_active", True)
        if not is_active or stock < total_quantity:
            raise ProductNotAvailableException()

        item = await self.cart_service.add_item(
            cart=cart,
            product_id=request.product_id,
            quantity=request.quantity,
            unit_price=float(product.get("price", 0)),
            product_title=product.get("title", ""),
            product_image_url=product.get("image_url"),
        )

        return CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            product_title=item.product_title,
            product_image_url=item.product_image_url,
            subtotal=item.unit_price * item.quantity,
        )
