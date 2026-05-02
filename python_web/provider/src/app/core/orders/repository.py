"""Abstract repository interface for vendor order persistence.

Defines the protocol that all vendor order repository implementations must follow.
"""

from typing import Protocol
from uuid import UUID

from src.app.core.orders.entities import VendorOrder, VendorOrderStatus


class IVendorOrderRepository(Protocol):
    """Repository protocol for managing vendor orders.

    Implementations must provide async methods for CRUD operations
    on vendor order data.
    """

    async def create(self, order: VendorOrder) -> VendorOrder:
        """Persist a new vendor order.

        Args:
            order: The vendor order entity to create.

        Returns:
            The created vendor order with generated fields populated.
        """
        ...

    async def get_by_id(self, vendor_order_id: UUID) -> VendorOrder | None:
        """Get a vendor order by its unique ID.

        Args:
            vendor_order_id: UUID of the vendor order.

        Returns:
            The vendor order entity, or None if not found.
        """
        ...

    async def get_by_supplier_id(
        self,
        supplier_id: int,
        status: VendorOrderStatus | None,
        offset: int,
        limit: int,
    ) -> tuple[list[VendorOrder], int]:
        """Get paginated vendor orders for a supplier.

        Args:
            supplier_id: ID of the vendor.
            status: Optional status filter.
            offset: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            Tuple of (list of vendor orders, total count).
        """
        ...

    async def update_status(
        self, vendor_order_id: UUID, status: VendorOrderStatus
    ) -> VendorOrder | None:
        """Update the status of a vendor order.

        Args:
            vendor_order_id: UUID of the vendor order.
            status: New status value.

        Returns:
            The updated vendor order, or None if not found.
        """
        ...

    async def exists(self, order_id: UUID, supplier_id: int) -> bool:
        """Check whether a vendor order exists for the given order and supplier.

        Args:
            order_id: UUID of the parent customer order.
            supplier_id: ID of the vendor.

        Returns:
            True if a matching vendor order exists.
        """
        ...
