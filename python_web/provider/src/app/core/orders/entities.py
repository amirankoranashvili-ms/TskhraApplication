"""Domain entities for the vendor order bounded context.

Defines the vendor order model, order item model, and order status
enumeration for tracking vendor-specific order fulfillment.
"""

import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VendorOrderStatus(str, enum.Enum):
    """Lifecycle status of a vendor order."""

    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"


class VendorOrderItem(BaseModel):
    """Represents a single line item within a vendor order.

    Attributes:
        id: Unique identifier for the order item.
        vendor_order_id: ID of the parent vendor order.
        product_id: ID of the product in the catalog.
        quantity: Number of units ordered.
        unit_price: Price per unit at the time of purchase.
        product_title: Display title of the product.
    """

    id: UUID
    vendor_order_id: UUID
    product_id: int
    quantity: int
    unit_price: float
    product_title: str

    model_config = ConfigDict(from_attributes=True)


class VendorOrder(BaseModel):
    """Represents a vendor's portion of a customer order.

    Attributes:
        id: Unique identifier for the vendor order.
        order_id: ID of the parent customer order.
        supplier_id: ID of the vendor fulfilling the order.
        buyer_user_id: UUID of the buyer.
        status: Current fulfillment status.
        vendor_subtotal: Total amount for this vendor's items.
        items: Line items in this vendor order.
        created_at: Timestamp of order creation.
        updated_at: Timestamp of last update.
    """

    id: UUID
    order_id: UUID
    supplier_id: int
    buyer_user_id: UUID
    status: VendorOrderStatus = VendorOrderStatus.PAID
    vendor_subtotal: float = 0.0
    items: list[VendorOrderItem] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
