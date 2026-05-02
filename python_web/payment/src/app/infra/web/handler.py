"""Pre-built OpenAPI error response definitions for payment endpoints."""

from backend_common.error_handlers import error_response

OrderNotFoundResponse = error_response(404, "NOT_FOUND", "Order not found.")
OrderAlreadyPaidResponse = error_response(
    409, "CONFLICT", "Order has already been paid."
)
OrderNotPayableResponse = error_response(
    422, "VALIDATION_ERROR", "Order cannot be paid in its current status."
)
OrderAccessDeniedResponse = error_response(
    403, "FORBIDDEN", "You do not have access to this order."
)
PaymentFailedResponse = error_response(
    500, "PAYMENT_FAILED", "Payment processing failed."
)
