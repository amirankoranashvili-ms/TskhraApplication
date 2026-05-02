"""Request schemas for payment service API endpoints."""

from decimal import Decimal
from urllib.parse import urlparse
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.app.core.config import settings


class BaseSchema(BaseModel):
    """Base schema with common configuration for all request models."""

    model_config = ConfigDict(str_strip_whitespace=True)


def validate_redirect_uri(url: str | None) -> str | None:
    if url is None:
        return None
    allowed = settings.keepz_allowed_redirect_origins
    if not allowed:
        raise ValueError("redirect URI not allowed: no allowed origins configured")
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in allowed:
        raise ValueError(f"redirect URI origin not allowed: {origin}")
    return url


class OrderItemRequest(BaseSchema):
    entity_id: str
    quantity: int
    unit_price: Decimal
    product_title: str


class CreateOrderRequest(BaseSchema):
    user_id: UUID
    items: list[OrderItemRequest]
    total_amount: Decimal


class WebhookPayload(BaseSchema):
    """Incoming webhook payload from KeepZ."""

    integratorOrderId: str
    status: str
    amount: Decimal | None = None
    integratorId: str | None = None
    receiverId: str | None = None
