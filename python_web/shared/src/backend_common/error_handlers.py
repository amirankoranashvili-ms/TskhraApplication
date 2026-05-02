"""FastAPI exception handler registration and OpenAPI error response helpers.

Maps application error codes to HTTP status codes and provides utilities
for generating consistent JSON error responses across all services.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend_common.exceptions import BaseAppException

ERROR_CODE_TO_HTTP: dict[str, int] = {
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "USER_ALREADY_EXISTS": 409,
    "USER_ALREADY_VERIFIED": 409,
    "FORBIDDEN": 403,
    "VALIDATION_ERROR": 422,
    "COOLDOWN_ACTIVE": 429,
    "CODE_EXPIRED": 410,
    "INVALID_CODE": 400,
    "TOO_MANY_ATTEMPTS": 429,
    "INVALID_CREDENTIALS": 401,
    "ACCOUNT_NOT_VERIFIED": 403,
    "IDENTICAL_PASSWORD": 400,
    "INVALID_RESET_TOKEN": 400,
    "EXTERNAL_SERVICE_ERROR": 502,
    "UNAUTHORIZED": 401,
    "INTERNAL_ERROR": 500,
    "SELLER_NOT_FOUND": 404,
    "SELLER_ALREADY_EXISTS": 409,
    "SELLER_REGISTRATION_PENDING": 409,
    "SELLER_DATA_UNCHANGED": 422,
    "ID_NUMBER_ALREADY_REGISTERED": 409,
    "INVALID_IBAN": 422,
    "IBAN_VALIDATION_UNAVAILABLE": 503,
    "INVALID_ID_NUMBER": 422,
    "ID_VALIDATION_UNAVAILABLE": 503,
    "TASK_NOT_FOUND": 404,
    "TASK_NOT_DRAFT": 409,
    "DRAFT_ALREADY_EXISTS": 409,
    "NO_IMAGES": 422,
    "TOO_MANY_IMAGES": 422,
    "IMAGE_NOT_IN_DRAFT": 400,
    "PROFILE_NOT_FOUND": 404,
    "INVALID_AVATAR": 400,
    "AVATAR_CONFLICT": 400,
    "INVALID_AGE": 400,
    "AVATAR_NOT_FOUND": 404,
    "AVATAR_NOT_PROVIDED": 400,
    "FILE_TOO_LARGE": 413,
    "INVALID_FILE_TYPE": 400,
    "LISTING_NOT_FOUND": 404,
    "LISTING_FORBIDDEN": 403,
    "VENDOR_PRODUCT_ERROR": 400,
    "CATALOG_SERVICE_UNAVAILABLE": 503,
    "PRODUCT_DATA_UNCHANGED": 422,
    "CART_ITEM_NOT_FOUND": 404,
    "PRODUCT_NOT_AVAILABLE": 400,
    "INSUFFICIENT_STOCK": 400,
    "PRODUCT_ALREADY_IN_CART": 409,
    "VENDOR_ORDER_NOT_FOUND": 404,
    "INVALID_STATUS_TRANSITION": 422,
    "LISTING_LOCKED": 409,
    "TRADE_NOT_FOUND": 404,
    "TRADE_ALREADY_RESOLVED": 409,
    "TRADE_PARTICIPANT_NOT_FOUND": 404,
    "DELIVERY_FAILED": 502,
    "NO_DELIVERY_CHANNEL": 422,
    "PROPOSAL_NOT_FOUND": 404,
    "PROPOSAL_SESSION_NOT_FOUND": 404,
    "PROPOSAL_SESSION_EXPIRED": 410,
    "INVALID_DRAFT_DATA": 422,
    "CITY_NOT_FOUND": 404,
    "PROVIDER_NOT_FOUND": 404,
    "PROVIDER_ALREADY_EXISTS": 409,
    "AVAILABILITY_NOT_FOUND": 404,
    "AVAILABILITY_CONFLICT": 409,
    "BRANCH_LIMIT_EXCEEDED": 409,
    "AVAILABILITY_VALIDATION": 422,
    "SERVICE_NOT_FOUND": 404,
    "SERVICE_FORBIDDEN": 403,
    "RESOURCE_NOT_FOUND": 404,
    "SERVICE_CAPACITY_EXCEEDED": 409,
    "INDIVIDUAL_RESOURCE_LIMIT": 422,
    "INDIVIDUAL_CAPACITY_LIMIT": 422,
    "BOOKING_NOT_FOUND": 404,
    "BOOKING_FORBIDDEN": 403,
    "SLOT_NOT_AVAILABLE": 409,
    "BOOKING_CANCEL_TOO_LATE": 400,
    "BOOKING_RESCHEDULE_NOT_ALLOWED": 409,
    "SERIES_NOT_FOUND": 404,
    "SERIES_FORBIDDEN": 403,
    "SERIES_PARTIAL_UNAVAILABLE": 409,
}


async def app_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    """Convert a BaseAppException into a structured JSON error response.

    Args:
        request: The incoming FastAPI request.
        exc: The application exception to handle.

    Returns:
        A JSONResponse with the appropriate HTTP status code, error code, and message.
    """
    status_code = ERROR_CODE_TO_HTTP.get(exc.error_code, 500)
    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.context if exc.context else None,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register the global application exception handler on a FastAPI app.

    Args:
        app: The FastAPI application instance.
    """
    app.add_exception_handler(BaseAppException, app_exception_handler)


def merge_responses(*responses: dict) -> dict:
    """Merge multiple OpenAPI response dictionaries into one.

    Args:
        *responses: Response dicts keyed by HTTP status code.

    Returns:
        A single merged dictionary of all response definitions.
    """
    merged: dict = {}
    for r in responses:
        merged.update(r)
    return merged


def error_response(status_code: int, error_code: str, message: str) -> dict:
    """Build an OpenAPI-compatible error response definition.

    Args:
        status_code: The HTTP status code for this error.
        error_code: Machine-readable error code string.
        message: Human-readable error description.

    Returns:
        A dict suitable for use in FastAPI ``responses`` parameter.
    """
    return {
        status_code: {
            "description": message,
            "content": {
                "application/json": {
                    "example": {
                        "error_code": error_code,
                        "message": message,
                    }
                }
            },
        }
    }
