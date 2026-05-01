"""Pre-built error response definitions for cart API error documentation.

Provides standardized error response schemas used in OpenAPI documentation
for cart-related endpoints.
"""

from backend_common.error_handlers import error_response

CartNotFoundResponse = error_response(404, "NOT_FOUND", "Cart not found.")
CartItemNotFoundResponse = error_response(404, "NOT_FOUND", "Cart item not found.")
CartCheckedOutResponse = error_response(
    409, "CONFLICT", "Cart has already been checked out."
)
CartEmptyResponse = error_response(
    422, "VALIDATION_ERROR", "Cannot checkout an empty cart."
)
InvalidQuantityResponse = error_response(
    422, "VALIDATION_ERROR", "Quantity must be greater than 0."
)
ProductNotAvailableResponse = error_response(
    422, "VALIDATION_ERROR", "Product is not available or insufficient stock."
)
ExternalServiceResponse = error_response(
    502, "EXTERNAL_SERVICE_ERROR", "External service is unavailable."
)
