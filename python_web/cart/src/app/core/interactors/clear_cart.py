"""Interactor for clearing all items from the user's cart."""

from uuid import UUID

from backend_common.schemas import MessageResponse

from src.app.core.cart.service import CartService


class ClearCartInteractor:
    """Use case for removing all items from the shopping cart."""

    def __init__(self, cart_service: CartService) -> None:
        self.cart_service = cart_service

    async def execute(self, user_id: UUID) -> MessageResponse:
        """Clear all items from the user's active cart.

        Args:
            user_id: The authenticated user's identifier.

        Returns:
            A message confirming the cart was cleared.
        """
        cart = await self.cart_service.get_or_create_cart(user_id)
        await self.cart_service.clear_cart(cart)
        return MessageResponse(message="Cart cleared.")
