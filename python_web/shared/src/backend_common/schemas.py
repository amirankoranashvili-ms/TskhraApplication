"""Shared Pydantic response schemas used across all backend services.

Defines standard API response models for success messages, errors,
and paginated collections.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Simple response containing a human-readable message.

    Attributes:
        message: The response message text.
    """

    message: str


class ErrorResponse(BaseModel):
    """Structured error response returned by API endpoints.

    Attributes:
        error_code: Machine-readable error identifier.
        message: Human-readable error description.
        details: Optional additional error context.
    """

    error_code: str
    message: str
    details: dict | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper for list endpoints.

    Attributes:
        items: The page of results.
        total: Total number of items across all pages.
        page: Current page number (1-based).
        limit: Maximum items per page.
        total_pages: Total number of pages.
    """

    items: list[T]
    total: int
    page: int
    limit: int
    total_pages: int