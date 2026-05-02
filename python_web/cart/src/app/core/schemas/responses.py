"""Response schemas for cart API endpoints.

Defines Pydantic models for serializing cart data in API responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CartItemResponse(BaseModel):
    """Response model for a single cart item with computed subtotal."""

    id: UUID
    product_id: int
    quantity: int
    unit_price: float
    product_title: str
    product_image_url: str | None = None
    subtotal: float = 0.0
    stock_quantity: int | None = None


class CartResponse(BaseModel):
    """Response model for the full shopping cart."""

    id: UUID
    user_id: UUID
    items: list[CartItemResponse] = []
    status: str
    total: float = 0.0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CheckoutResponse(BaseModel):
    """Response model for a completed checkout operation."""

    cart_id: UUID
    status: str
    total: float
    item_count: int
    message: str
