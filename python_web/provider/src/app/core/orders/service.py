"""Service layer for vendor order management.

Handles order creation from payment events, order retrieval,
and status transitions with validation.
"""

import logging
import uuid
from uuid import UUID

from src.app.core.orders.entities import VendorOrder, VendorOrderItem, VendorOrderStatus
from src.app.core.orders.exceptions import (
    InvalidOrderStatusTransitionException,
    VendorOrderNotFoundException,
)
from src.app.core.orders.repository import IVendorOrderRepository
from src.app.core.ports.event_publisher import IEventPublisher

logger = logging.getLogger(__name__)

VALID_TRANSITIONS: dict[VendorOrderStatus, list[VendorOrderStatus]] = {
    VendorOrderStatus.PAID: [VendorOrderStatus.PROCESSING],
    VendorOrderStatus.PROCESSING: [VendorOrderStatus.SHIPPED],
    VendorOrderStatus.SHIPPED: [VendorOrderStatus.DELIVERED],
    VendorOrderStatus.DELIVERED: [],
}


class VendorOrderService:
    """Service for vendor order lifecycle management.

    Manages order creation from payment events, pagination queries,
    and status transitions with valid transition enforcement.
    """

    def __init__(
        self,
        repository: IVendorOrderRepository,
        publisher: IEventPublisher | None = None,
    ) -> None:
        """Initialize the vendor order service.

        Args:
            repository: Vendor order repository implementation.
            publisher: Optional event publisher for status change events.
        """
        self.repository = repository
        self.publisher = publisher

    async def create_from_payment_event(
        self,
        order_id: UUID,
        buyer_user_id: UUID,
        supplier_id: int,
        items: list[dict],
    ) -> VendorOrder | None:
        """Create a vendor order from a payment confirmation event.

        Args:
            order_id: UUID of the parent customer order.
            buyer_user_id: UUID of the buyer.
            supplier_id: ID of the vendor.
            items: List of item dicts with product_id, quantity, unit_price.

        Returns:
            The created vendor order, or None if it already exists.
        """
        if await self.repository.exists(order_id, supplier_id):
            logger.info(
                "VendorOrder already exists for order=%s supplier=%s, skipping",
                order_id,
                supplier_id,
            )
            return None

        vendor_order_id = uuid.uuid4()
        vendor_subtotal = sum(item["quantity"] * item["unit_price"] for item in items)

        order_items = [
            VendorOrderItem(
                id=uuid.uuid4(),
                vendor_order_id=vendor_order_id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                product_title=item.get("product_title", ""),
            )
            for item in items
        ]

        vendor_order = VendorOrder(
            id=vendor_order_id,
            order_id=order_id,
            supplier_id=supplier_id,
            buyer_user_id=buyer_user_id,
            status=VendorOrderStatus.PAID,
            vendor_subtotal=vendor_subtotal,
            items=order_items,
        )

        return await self.repository.create(vendor_order)

    async def get_orders(
        self,
        supplier_id: int,
        status: VendorOrderStatus | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[VendorOrder], int]:
        """Get paginated vendor orders with optional status filter.

        Args:
            supplier_id: ID of the vendor.
            status: Optional status to filter by.
            page: Page number (1-based).
            limit: Number of orders per page.

        Returns:
            Tuple of (orders list, total count).
        """
        offset = (page - 1) * limit
        return await self.repository.get_by_supplier_id(
            supplier_id, status, offset, limit
        )

    async def get_order(self, vendor_order_id: UUID) -> VendorOrder:
        """Get a single vendor order by ID.

        Args:
            vendor_order_id: UUID of the vendor order.

        Returns:
            The vendor order entity.

        Raises:
            VendorOrderNotFoundException: If the order does not exist.
        """
        order = await self.repository.get_by_id(vendor_order_id)
        if not order:
            raise VendorOrderNotFoundException()
        return order

    async def update_status(
        self, vendor_order_id: UUID, new_status: VendorOrderStatus
    ) -> VendorOrder:
        """Update the status of a vendor order.

        Args:
            vendor_order_id: UUID of the vendor order.
            new_status: Target status to transition to.

        Returns:
            The updated vendor order.

        Raises:
            VendorOrderNotFoundException: If the order does not exist.
            InvalidOrderStatusTransitionException: If the transition is invalid.
        """
        order = await self.get_order(vendor_order_id)

        allowed = VALID_TRANSITIONS.get(order.status, [])
        if new_status not in allowed:
            raise InvalidOrderStatusTransitionException()

        updated = await self.repository.update_status(vendor_order_id, new_status)
        if not updated:
            raise VendorOrderNotFoundException()

        if self.publisher:
            await self.publisher.publish_order_status_updated(
                {
                    "vendor_order_id": str(updated.id),
                    "order_id": str(updated.order_id),
                    "supplier_id": updated.supplier_id,
                    "status": new_status.value,
                }
            )

        return updated
