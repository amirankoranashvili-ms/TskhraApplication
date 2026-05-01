"""Shared application exception hierarchy.

Provides a base exception class with error codes and contextual data,
along with domain-specific subclasses used across all backend services.
"""

from typing import Any


class BaseAppException(Exception):
    """Base exception for all application-level errors.

    Attributes:
        error_code: Machine-readable error identifier mapped to HTTP status codes.
        message: Human-readable error description.
        context: Arbitrary key-value pairs providing additional error details.
    """

    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, **context: Any) -> None:
        """Initialize the exception with an optional message and context.

        Args:
            message: Override the default error message.
            **context: Additional context data included in API error responses.
        """
        self.message = message or self.message
        self.context = context
        super().__init__(self.message)


class EntityNotFoundException(BaseAppException):
    """Raised when a requested entity does not exist."""

    error_code = "NOT_FOUND"
    message = "Entity not found."


class ConflictException(BaseAppException):
    """Raised when a resource already exists or conflicts with current state."""

    error_code = "CONFLICT"
    message = "Resource already exists."


class ForbiddenException(BaseAppException):
    """Raised when the user lacks permission for the requested action."""

    error_code = "FORBIDDEN"
    message = "You do not have permission to perform this action."


class ValidationException(BaseAppException):
    """Raised when input validation fails."""

    error_code = "VALIDATION_ERROR"
    message = "Validation failed."


class CooldownActiveException(BaseAppException):
    """Raised when an action is attempted during an active cooldown period."""

    error_code = "COOLDOWN_ACTIVE"
    message = "Please wait before retrying."


class CodeExpiredException(BaseAppException):
    """Raised when a verification code has expired."""

    error_code = "CODE_EXPIRED"
    message = "Verification code has expired."


class InvalidCodeException(BaseAppException):
    """Raised when a provided verification code does not match."""

    error_code = "INVALID_CODE"
    message = "Invalid verification code."


class TooManyAttemptsException(BaseAppException):
    """Raised when the maximum number of verification attempts is exceeded."""

    error_code = "TOO_MANY_ATTEMPTS"
    message = "Too many failed attempts."


class ExternalServiceException(BaseAppException):
    """Raised when an external service call fails or is unavailable."""

    error_code = "EXTERNAL_SERVICE_ERROR"
    message = "External service is unavailable."


class NotAuthenticatedException(BaseAppException):
    """Raised when a request lacks valid authentication credentials."""

    error_code = "UNAUTHORIZED"
    message = "Not authenticated."


class FileTooLargeException(BaseAppException):
    """Raised when an uploaded file exceeds the maximum allowed size."""

    error_code = "FILE_TOO_LARGE"
    message = "File too large."

    def __init__(self, max_size_mb: int = 5) -> None:
        """Initialize with the maximum allowed file size.

        Args:
            max_size_mb: Maximum file size in megabytes.
        """
        super().__init__(f"File too large. Maximum size is {max_size_mb} MB.")


class InvalidFileTypeException(BaseAppException):
    """Raised when an uploaded file has a disallowed MIME type."""

    error_code = "INVALID_FILE_TYPE"
    message = "Invalid file type."

    def __init__(self, mime_type: str = "unknown") -> None:
        """Initialize with the rejected MIME type.

        Args:
            mime_type: The MIME type that was rejected.
        """
        super().__init__(f"Invalid file type: {mime_type}. Only images are allowed.")