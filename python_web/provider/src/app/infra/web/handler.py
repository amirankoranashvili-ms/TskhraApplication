"""API error response definitions for OpenAPI documentation.

Defines pre-built error response schemas for common error scenarios,
used in FastAPI endpoint `responses` parameters for OpenAPI spec generation.
"""

from backend_common.error_handlers import (
    error_response,
)

SellerAlreadyExistsResponse = error_response(
    409, "SELLER_ALREADY_EXISTS", "Seller already exists."
)
SellerRegistrationPendingResponse = error_response(
    409, "SELLER_REGISTRATION_PENDING", "Seller registration is pending admin approval."
)
SellerDataUnchangedResponse = error_response(
    422, "SELLER_DATA_UNCHANGED", "Please submit different data to reapply."
)
SellerNotFoundResponse = error_response(
    404, "SELLER_NOT_FOUND", "Seller profile not found."
)
NotAuthenticatedResponse = error_response(401, "UNAUTHORIZED", "Not authenticated.")
KycVerificationRequiredResponse = error_response(
    403, "KYC_REQUIRED", "KYC verification required."
)
InvalidIbanResponse = error_response(
    422, "INVALID_IBAN", "Invalid IBAN account number."
)
InvalidIdentificationNumberResponse = error_response(
    422,
    "INVALID_ID_NUMBER",
    "Identification number not found in the business registry.",
)
VendorProductErrorResponse = error_response(
    400, "VENDOR_PRODUCT_ERROR", "Product operation failed."
)
ProductDataUnchangedResponse = error_response(
    422,
    "PRODUCT_DATA_UNCHANGED",
    "Please submit different data to resubmit rejected product.",
)
CatalogServiceUnavailableResponse = error_response(
    503,
    "CATALOG_SERVICE_UNAVAILABLE",
    "The main catalog service is currently unreachable.",
)
ImageNotFoundResponse = error_response(404, "NOT_FOUND", "Image not found.")
TaskNotFoundResponse = error_response(404, "TASK_NOT_FOUND", "Task not found.")
TaskNotDraftResponse = error_response(
    409, "TASK_NOT_DRAFT", "Task is not in Draft status."
)
NoImagesResponse = error_response(
    422, "NO_IMAGES", "At least one image is required to submit."
)
DraftAlreadyExistsResponse = error_response(
    409, "DRAFT_ALREADY_EXISTS", "A draft already exists for this product."
)
InvalidDraftDataResponse = error_response(
    422, "INVALID_DRAFT_DATA", "Draft is missing required fields."
)
VendorOrderNotFoundResponse = error_response(
    404, "VENDOR_ORDER_NOT_FOUND", "Vendor order not found."
)
InvalidStatusTransitionResponse = error_response(
    422, "INVALID_STATUS_TRANSITION", "Invalid order status transition."
)
