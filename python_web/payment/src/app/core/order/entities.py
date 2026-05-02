"""Domain entities for the order bounded context."""

import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrderStatus(str, enum.Enum):
    """Enumeration of possible order lifecycle states."""

    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class OrderItem(BaseModel):
    """A single line item within an order."""

    id: UUID
    order_id: UUID
    entity_id: str
    quantity: int
    unit_price: Decimal
    product_title: str

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    """Aggregate root representing a customer order."""

    id: UUID
    user_id: UUID
    items: list[OrderItem] = []
    status: OrderStatus = OrderStatus.PENDING
    total_amount: Decimal = Decimal("0")
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
