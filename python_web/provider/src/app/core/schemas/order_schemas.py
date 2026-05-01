"""Request and response schemas for vendor order API endpoints.

Defines Pydantic models for order status updates, order detail responses,
and paginated order listing responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.app.core.orders.entities import VendorOrderStatus


class UpdateOrderStatusRequest(BaseModel):
    """Request schema for updating a vendor order's status.

    Attributes:
        status: The target order status.
    """

    status: VendorOrderStatus


class VendorOrderItemResponse(BaseModel):
    """Response schema for a single order line item.

    Attributes:
        id: Unique item identifier.
        product_id: Catalog product ID.
        quantity: Number of units.
        unit_price: Price per unit.
        product_title: Display title of the product.
    """

    id: UUID
    product_id: int
    quantity: int
    unit_price: float
    product_title: str


class VendorOrderResponse(BaseModel):
    """Response schema for a single vendor order with items.

    Attributes:
        id: Vendor order UUID.
        order_id: Parent customer order UUID.
        supplier_id: Vendor identifier.
        buyer_user_id: Buyer's user UUID.
        status: Current order status.
        vendor_subtotal: Total amount for this vendor.
        items: List of order line items.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: UUID
    order_id: UUID
    supplier_id: int
    buyer_user_id: UUID
    status: VendorOrderStatus
    vendor_subtotal: float
    items: list[VendorOrderItemResponse]
    created_at: datetime | None = None
    updated_at: datetime | None = None


class VendorOrderPaginatedResponse(BaseModel):
    """Paginated response schema for vendor order listings.

    Attributes:
        orders: List of vendor orders for the current page.
        total: Total number of matching orders.
        page: Current page number.
        limit: Items per page.
    """

    orders: list[VendorOrderResponse]
    total: int
    page: int
    limit: int
