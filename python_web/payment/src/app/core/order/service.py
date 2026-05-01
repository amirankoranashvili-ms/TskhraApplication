"""Application service encapsulating order business rules."""

import uuid
from decimal import Decimal
from uuid import UUID

from src.app.core.order.entities import Order, OrderItem, OrderStatus
from src.app.core.order.exceptions import (
    OrderAccessDeniedException,
    OrderNotFoundException,
    OrderNotPayableException,
    OrderNotRefundableException,
)
from src.app.core.order.repository import IOrderRepository


class OrderService:
    """Manages order creation, retrieval, and status transitions."""

    def __init__(self, order_repository: IOrderRepository) -> None:
        """Initialize with an order repository.

        Args:
            order_repository: Repository for order persistence operations.
        """
        self.order_repository = order_repository

    async def create_order_from_checkout(
        self,
        user_id: UUID,
        items: list[dict],
        total_amount: Decimal,
    ) -> Order:
        """Create a new order from checkout data.

        Args:
            user_id: ID of the user placing the order.
            items: List of item dicts with product_id, quantity, unit_price, product_title.
            total_amount: Pre-calculated total for the order.

        Returns:
            The persisted Order entity.
        """
        order_id = uuid.uuid4()
        order_items = [
            OrderItem(
                id=uuid.uuid4(),
                order_id=order_id,
                entity_id=str(item.get("entity_id") or item.get("product_id", "")),
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                product_title=item["product_title"],
            )
            for item in items
        ]
        order = Order(
            id=order_id,
            user_id=user_id,
            items=order_items,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
        )
        return await self.order_repository.create(order)

    async def get_order(self, order_id: UUID, user_id: UUID | None = None) -> Order:
        """Retrieve an order by ID, optionally enforcing user ownership.

        Args:
            order_id: The order's unique identifier.
            user_id: If provided, verifies the order belongs to this user.

        Returns:
            The matching Order entity.

        Raises:
            OrderNotFoundException: If the order does not exist.
            OrderAccessDeniedException: If user_id does not match the order owner.
        """
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise OrderNotFoundException()
        if user_id and order.user_id != user_id:
            raise OrderAccessDeniedException()
        return order

    async def get_order_history(
        self, user_id: UUID, page: int = 1, limit: int = 20
    ) -> tuple[list[Order], int]:
        """Fetch paginated order history for a user.

        Args:
            user_id: The user whose orders to retrieve.
            page: Page number (1-based).
            limit: Maximum orders per page.

        Returns:
            Tuple of (list of orders, total count).
        """
        offset = (page - 1) * limit
        return await self.order_repository.get_by_user_id(user_id, offset, limit)

    async def update_order_status(self, order_id: UUID, status: OrderStatus) -> Order:
        """Update an order's status.

        Args:
            order_id: The order to update.
            status: The new status value.

        Returns:
            The updated Order entity.

        Raises:
            OrderNotFoundException: If the order does not exist.
        """
        order = await self.order_repository.update_status(order_id, status)
        if not order:
            raise OrderNotFoundException()
        return order

    async def mark_as_paid(self, order_id: UUID) -> Order:
        """Transition an order to PAID status.

        Args:
            order_id: The order to mark as paid.

        Returns:
            The updated Order entity.

        Raises:
            OrderNotPayableException: If the order is not in PENDING status.
        """
        order = await self.get_order(order_id)
        if order.status != OrderStatus.PENDING:
            raise OrderNotPayableException()
        return await self.update_order_status(order_id, OrderStatus.PAID)

    async def mark_as_refunded(self, order_id: UUID) -> Order:
        """Transition an order to REFUNDED status.

        Args:
            order_id: The order to refund.

        Returns:
            The updated Order entity.

        Raises:
            OrderNotRefundableException: If the order is not in PAID or SHIPPED status.
        """
        order = await self.get_order(order_id)
        if order.status not in (OrderStatus.PAID, OrderStatus.SHIPPED):
            raise OrderNotRefundableException()
        return await self.update_order_status(order_id, OrderStatus.REFUNDED)
