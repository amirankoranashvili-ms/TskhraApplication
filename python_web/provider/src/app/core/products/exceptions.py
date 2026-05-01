"""Exception classes for product domain operations.

Each exception maps to a specific error scenario in the product upload,
update, and image management workflows.
"""

from backend_common.exceptions import (
    BaseAppException,
    ConflictException,
    EntityNotFoundException,
    ValidationException,
)


class VendorProductException(BaseAppException):
    """Raised for general product operation failures."""

    error_code = "VENDOR_PRODUCT_ERROR"
    message = "Product operation failed."


class CatalogServiceUnavailableException(BaseAppException):
    """Raised when the catalog service is unreachable."""

    error_code = "CATALOG_SERVICE_UNAVAILABLE"
    message = (
        "The main catalog service is currently unreachable. Please try again later."
    )


class TooManyImagesException(ValidationException):
    """Raised when uploading would exceed the maximum image count."""

    error_code = "TOO_MANY_IMAGES"
    message = "Too many images."

    def __init__(self, max_images: int) -> None:
        """Initialize with the maximum allowed image count.

        Args:
            max_images: Maximum number of images permitted.
        """
        super().__init__(f"Too many images. Maximum allowed is {max_images}.")


class ProductDataUnchangedException(ValidationException):
    """Raised when resubmitting a rejected product with unchanged data."""

    error_code = "PRODUCT_DATA_UNCHANGED"
    message = "Please submit different data to resubmit rejected product."


class TaskNotFoundException(EntityNotFoundException):
    """Raised when a product upload task cannot be found."""

    error_code = "TASK_NOT_FOUND"
    message = "Task not found."


class TaskNotDraftException(ConflictException):
    """Raised when an operation requires Draft status but the task is not."""

    error_code = "TASK_NOT_DRAFT"
    message = "Task is not in Draft status."


class NoImagesException(ValidationException):
    """Raised when submitting a product with no images attached."""

    error_code = "NO_IMAGES"
    message = "At least one image is required to submit."


class DraftAlreadyExistsException(ConflictException):
    """Raised when a draft already exists for the target product."""

    error_code = "DRAFT_ALREADY_EXISTS"
    message = "A draft already exists for this product."


class ImageNotInDraftException(BaseAppException):
    """Raised when attempting to delete images not present in the draft."""

    error_code = "IMAGE_NOT_IN_DRAFT"
    message = "One or more images not found in draft."


class InvalidDraftDataException(ValidationException):
    """Raised when draft payload is missing required fields for submission."""

    error_code = "INVALID_DRAFT_DATA"
    message = "Draft is missing required fields."

    def __init__(self, errors: list[dict]) -> None:
        details = "; ".join(
            f"{'.'.join(str(part) for part in e.get('loc', []))}: {e.get('msg', '')}"
            for e in errors
        )
        super().__init__(f"Draft validation failed: {details}")
