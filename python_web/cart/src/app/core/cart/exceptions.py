"""Custom exception classes for the cart domain.

Defines domain-specific exceptions for cart operations such as
not-found errors, validation failures, and conflict states.
"""

from backend_common.exceptions import (
    BaseAppException,
    EntityNotFoundException,
    ValidationException,
)


class CartNotFoundException(EntityNotFoundException):
    """Raised when a requested cart cannot be found."""

    error_code = "NOT_FOUND"
    message = "Cart not found."


class CartItemNotFoundException(EntityNotFoundException):
    """Raised when a requested cart item cannot be found."""

    error_code = "NOT_FOUND"
    message = "Cart item not found."


class CartAlreadyCheckedOutException(BaseAppException):
    """Raised when an operation is attempted on a non-active cart."""

    error_code = "CONFLICT"
    message = "Cart has already been checked out."


class CartEmptyException(ValidationException):
    """Raised when attempting to checkout an empty cart."""

    error_code = "VALIDATION_ERROR"
    message = "Cannot checkout an empty cart."


class InvalidQuantityException(ValidationException):
    """Raised when a quantity value is not positive."""

    error_code = "VALIDATION_ERROR"
    message = "Quantity must be greater than 0."


class ProductNotAvailableException(ValidationException):
    """Raised when a product is unavailable or has insufficient stock."""

    error_code = "VALIDATION_ERROR"
    message = "Product is not available or insufficient stock."
