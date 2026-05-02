"""Cart domain service implementing core business logic.

Provides operations for managing shopping carts, including item management,
total calculation, and checkout processing.
"""

import logging
import uuid
from uuid import UUID

from src.app.core.cart.entities import Cart, CartItem, CartStatus
from src.app.core.cart.exceptions import (
    CartAlreadyCheckedOutException,
    CartEmptyException,
    CartItemNotFoundException,
    InvalidQuantityException,
)
from src.app.core.cart.repository import ICartRepository

logger = logging.getLogger(__name__)


class CartService:
    """Domain service encapsulating cart business rules."""

    def __init__(self, cart_repository: ICartRepository) -> None:
        """Initialize the cart service.

        Args:
            cart_repository: Repository for cart persistence operations.
        """
        self.cart_repository = cart_repository

    async def get_or_create_cart(self, user_id: UUID) -> Cart:
        """Retrieve the user's active cart or create a new one.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The user's active cart.
        """
        cart = await self.cart_repository.get_active_cart_by_user(user_id)
        if cart:
            return cart

        new_cart = Cart(
            id=uuid.uuid4(),
            user_id=user_id,
            items=[],
            status=CartStatus.ACTIVE,
        )
        return await self.cart_repository.create(new_cart)

    async def get_item_by_product(
        self, cart_id: UUID, product_id: int
    ) -> CartItem | None:
        """Find a cart item by product ID within a cart.

        Args:
            cart_id: The cart's unique identifier.
            product_id: The product identifier to look up.

        Returns:
            The cart item if found, or None.
        """
        return await self.cart_repository.get_item_by_product(cart_id, product_id)

    async def add_item(
        self,
        cart: Cart,
        product_id: int,
        quantity: int,
        unit_price: float,
        product_title: str,
        product_image_url: str | None = None,
    ) -> CartItem:
        """Add a product to the cart or update quantity if it already exists.

        Args:
            cart: The cart to add the item to.
            product_id: The product identifier.
            quantity: Number of units to add.
            unit_price: Price per unit of the product.
            product_title: Display title of the product.
            product_image_url: Optional URL to the product image.

        Returns:
            The created or updated cart item.

        Raises:
            InvalidQuantityException: If quantity is not positive.
            CartAlreadyCheckedOutException: If the cart is not active.
        """
        if quantity <= 0:
            raise InvalidQuantityException()

        if cart.status != CartStatus.ACTIVE:
            raise CartAlreadyCheckedOutException()

        existing = await self.cart_repository.get_item_by_product(cart.id, product_id)
        if existing:
            existing.quantity += quantity
            existing.unit_price = unit_price
            return await self.cart_repository.update_item(existing)

        item = CartItem(
            id=uuid.uuid4(),
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            product_title=product_title,
            product_image_url=product_image_url,
        )
        result = await self.cart_repository.add_item(item)
        logger.info(
            "Item added to cart %s: product_id=%d, qty=%d",
            cart.id,
            product_id,
            quantity,
        )
        return result

    async def update_quantity(
        self, cart: Cart, item_id: UUID, quantity: int
    ) -> CartItem:
        """Update the quantity of a specific cart item.

        Args:
            cart: The cart containing the item.
            item_id: The identifier of the cart item to update.
            quantity: The new quantity value.

        Returns:
            The updated cart item.

        Raises:
            InvalidQuantityException: If quantity is not positive.
            CartAlreadyCheckedOutException: If the cart is not active.
            CartItemNotFoundException: If the item does not exist in the cart.
        """
        if quantity <= 0:
            raise InvalidQuantityException()

        if cart.status != CartStatus.ACTIVE:
            raise CartAlreadyCheckedOutException()

        item = await self.cart_repository.get_item_by_id(item_id, cart.id)
        if not item:
            raise CartItemNotFoundException()

        item.quantity = quantity
        return await self.cart_repository.update_item(item)

    async def remove_item(self, cart: Cart, item_id: UUID) -> None:
        """Remove an item from the cart.

        Args:
            cart: The cart containing the item.
            item_id: The identifier of the item to remove.

        Raises:
            CartAlreadyCheckedOutException: If the cart is not active.
            CartItemNotFoundException: If the item does not exist in the cart.
        """
        if cart.status != CartStatus.ACTIVE:
            raise CartAlreadyCheckedOutException()

        item = await self.cart_repository.get_item_by_id(item_id, cart.id)
        if not item:
            raise CartItemNotFoundException()

        await self.cart_repository.remove_item(item_id, cart.id)
        logger.info("Item removed from cart %s: item_id=%s", cart.id, item_id)

    def calculate_total(self, cart: Cart) -> float:
        """Calculate the total price of all items in the cart.

        Args:
            cart: The cart to calculate the total for.

        Returns:
            The sum of unit_price * quantity for all items.
        """
        return sum(item.unit_price * item.quantity for item in cart.items)

    async def clear_cart(self, cart: Cart) -> None:
        """Remove all items from the cart.

        Args:
            cart: The cart to clear.

        Raises:
            CartAlreadyCheckedOutException: If the cart is not active.
        """
        if cart.status != CartStatus.ACTIVE:
            raise CartAlreadyCheckedOutException()

        await self.cart_repository.clear_items(cart.id)
        logger.info("Cart %s cleared", cart.id)

    async def checkout_cart(self, cart: Cart) -> Cart:
        """Mark the cart as checked out.

        Args:
            cart: The cart to checkout.

        Returns:
            The updated cart with CHECKED_OUT status.

        Raises:
            CartAlreadyCheckedOutException: If the cart is not active.
            CartEmptyException: If the cart contains no items.
        """
        if cart.status != CartStatus.ACTIVE:
            raise CartAlreadyCheckedOutException()
        if not cart.items:
            raise CartEmptyException()

        cart.status = CartStatus.CHECKED_OUT
        result = await self.cart_repository.update(cart)
        logger.info("Cart %s checked out", cart.id)
        return result
