"""Custom exceptions for the payment domain."""

from backend_common.exceptions import (
    BaseAppException,
    ConflictException,
    EntityNotFoundException,
)


class PaymentNotFoundException(EntityNotFoundException):
    """Raised when a requested payment does not exist."""

    error_code = "NOT_FOUND"
    message = "Payment not found."


class PaymentFailedException(BaseAppException):
    """Raised when a payment charge or processing operation fails."""

    error_code = "PAYMENT_FAILED"
    message = "Payment processing failed."


class PaymentAlreadyCompletedException(ConflictException):
    """Raised when attempting to pay an order that already has a completed payment."""

    error_code = "CONFLICT"
    message = "Payment already completed for this order."


class RefundFailedException(BaseAppException):
    """Raised when a refund operation fails at the gateway."""

    error_code = "REFUND_FAILED"
    message = "Refund processing failed."
