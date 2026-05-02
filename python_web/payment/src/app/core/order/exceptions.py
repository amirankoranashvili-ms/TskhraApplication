"""Custom exceptions for the order domain."""

from backend_common.exceptions import (
    BaseAppException,
    ConflictException,
    EntityNotFoundException,
    ForbiddenException,
)


class OrderNotFoundException(EntityNotFoundException):
    """Raised when a requested order does not exist."""

    error_code = "NOT_FOUND"
    message = "Order not found."


class OrderAlreadyPaidException(ConflictException):
    """Raised when attempting to pay for an already-paid order."""

    error_code = "CONFLICT"
    message = "Order has already been paid."


class OrderNotPayableException(BaseAppException):
    """Raised when an order's current status does not allow payment."""

    error_code = "VALIDATION_ERROR"
    message = "Order cannot be paid in its current status."


class OrderNotRefundableException(BaseAppException):
    """Raised when an order's current status does not allow refund."""

    error_code = "VALIDATION_ERROR"
    message = "Order cannot be refunded in its current status."


class OrderAccessDeniedException(ForbiddenException):
    """Raised when a user attempts to access an order they do not own."""

    error_code = "FORBIDDEN"
    message = "You do not have access to this order."
