"""Domain entities for the payment bounded context."""

import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PaymentStatus(str, enum.Enum):
    """Enumeration of possible payment states."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(BaseModel):
    """Entity representing a payment transaction against an order."""

    id: UUID
    order_id: UUID
    amount: Decimal
    status: PaymentStatus = PaymentStatus.PENDING
    provider_payment_id: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentResult(BaseModel):
    """Result returned by a payment gateway after a charge attempt."""

    success: bool
    provider_payment_id: str | None = None
    error_message: str | None = None
    redirect_url: str | None = None
    requires_redirect: bool = False
