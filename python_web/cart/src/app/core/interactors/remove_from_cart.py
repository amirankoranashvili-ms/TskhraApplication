"""Interactor for removing an item from the user's cart."""

from uuid import UUID

from backend_common.schemas import MessageResponse

from src.app.core.cart.service import CartService


class RemoveFromCartInteractor:
    """Use case for removing a single item from the shopping cart."""

    def __init__(self, cart_service: CartService) -> None:
        """Initialize the interactor.

        Args:
            cart_service: Service for cart domain operations.
        """
        self.cart_service = cart_service

    async def execute(self, user_id: UUID, item_id: UUID) -> MessageResponse:
        """Remove an item from the user's cart.

        Args:
            user_id: The authenticated user's identifier.
            item_id: The identifier of the cart item to remove.

        Returns:
            A message confirming the item was removed.
        """
        cart = await self.cart_service.get_or_create_cart(user_id)
        await self.cart_service.remove_item(cart, item_id)
        return MessageResponse(message="Item removed from cart.")
