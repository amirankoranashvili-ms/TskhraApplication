"""Exception classes for vendor order domain operations.

Each exception maps to a specific error scenario in the order
management workflow.
"""

from backend_common.exceptions import EntityNotFoundException, ValidationException


class VendorOrderNotFoundException(EntityNotFoundException):
    """Raised when a requested vendor order does not exist."""

    error_code = "VENDOR_ORDER_NOT_FOUND"
    message = "Vendor order not found."


class InvalidOrderStatusTransitionException(ValidationException):
    """Raised when an order status transition violates the allowed state machine."""

    error_code = "INVALID_STATUS_TRANSITION"
    message = "Invalid order status transition."
