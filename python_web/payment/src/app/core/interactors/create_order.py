"""Interactor for creating orders from checkout events."""

import logging
from decimal import Decimal
from uuid import UUID

from src.app.core.facades.order_facade import OrderFacade

logger = logging.getLogger(__name__)


class CreateOrderInteractor:
    """Triggered by cart.checkout event consumer -> creates order via facade."""

    def __init__(self, facade: OrderFacade) -> None:
        """Initialize with the order facade.

        Args:
            facade: Facade coordinating order and payment operations.
        """
        self.facade = facade

    async def execute(self, payload: dict) -> None:
        """Create an order from a checkout event payload.

        Args:
            payload: Dictionary containing ``user_id``, ``items``, and
                ``total_amount`` from the cart checkout event.
        """
        user_id = UUID(payload["user_id"])
        items = payload["items"]
        total_amount = Decimal(str(payload["total_amount"]))

        order = await self.facade.create_order_from_checkout(
            user_id=user_id,
            items=items,
            total_amount=total_amount,
        )
        logger.info(
            "Order %s created from cart checkout for user %s",
            order.id,
            user_id,
        )
