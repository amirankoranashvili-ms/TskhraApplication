"""Abstract repository interface for order persistence."""

from typing import Protocol
from uuid import UUID

from src.app.core.order.entities import Order, OrderStatus


class IOrderRepository(Protocol):
    """Protocol defining the contract for order data access."""

    async def create(self, order: Order) -> Order:
        """Persist a new order.

        Args:
            order: The order entity to store.

        Returns:
            The persisted order with any generated fields populated.
        """
        ...

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Retrieve an order by its unique identifier.

        Args:
            order_id: The UUID of the order.

        Returns:
            The Order if found, otherwise None.
        """
        ...

    async def get_by_user_id(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Order], int]:
        """Retrieve paginated orders for a user.

        Args:
            user_id: The owner's UUID.
            offset: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            Tuple of (list of orders, total count).
        """
        ...

    async def update_status(self, order_id: UUID, status: OrderStatus) -> Order | None:
        """Update the status of an existing order.

        Args:
            order_id: The UUID of the order to update.
            status: The new order status.

        Returns:
            The updated Order if found, otherwise None.
        """
        ...
