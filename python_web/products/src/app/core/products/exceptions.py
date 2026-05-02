"""Product domain exceptions.

Custom exception classes raised when product or brand entities
cannot be found during business operations.
"""

from backend_common.exceptions import EntityNotFoundException


class ProductNotFoundException(EntityNotFoundException):
    """Raised when a requested product does not exist."""

    message = "Product not found."


class BrandNotFoundException(EntityNotFoundException):
    """Raised when a requested brand does not exist."""

    message = "Brand not found."
