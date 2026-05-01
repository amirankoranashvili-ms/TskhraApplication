"""Response schemas for payment service API endpoints."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, PlainSerializer

Amount = Annotated[
    Decimal, PlainSerializer(lambda x: float(x), return_type=float, when_used="json")
]


class OrderItemResponse(BaseModel):
    """Response model for a single order line item."""

    id: UUID
    entity_id: str
    quantity: int
    unit_price: Amount
    product_title: str


class OrderResponse(BaseModel):
    """Response model for an order with its items."""

    id: UUID
    user_id: UUID
    items: list[OrderItemResponse] = []
    status: str
    total_amount: Amount
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PaymentResponse(BaseModel):
    """Response model for payment details."""

    id: UUID
    order_id: UUID
    amount: Amount
    status: str
    provider_payment_id: str | None = None
    redirect_url: str | None = None
    created_at: datetime | None = None


class OrderWithPaymentResponse(OrderResponse):
    """Response model combining order details with associated payment info."""

    payment: PaymentResponse | None = None


class CreateOrderResponse(BaseModel):
    order_id: UUID


class OrderPaginatedResponse(BaseModel):
    """Paginated response wrapper for order listings."""

    items: list[OrderResponse]
    total: int
    page: int
    limit: int
    total_pages: int
