"""Domain entities for the cart bounded context.

Defines the core data models for shopping carts and cart items using
Pydantic, including the cart lifecycle status enumeration.
"""

import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CartStatus(str, enum.Enum):
    """Enumeration of possible cart lifecycle states."""

    ACTIVE = "ACTIVE"
    CHECKED_OUT = "CHECKED_OUT"
    EXPIRED = "EXPIRED"


class CartItem(BaseModel):
    """Represents a single item within a shopping cart."""

    id: UUID
    cart_id: UUID
    product_id: int
    quantity: int
    unit_price: float
    product_title: str
    product_image_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    """Represents a user's shopping cart with its collection of items."""

    id: UUID
    user_id: UUID
    items: list[CartItem] = []
    status: CartStatus = CartStatus.ACTIVE
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
