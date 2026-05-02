"""Pagination parameter parsing and result containers.

Provides a Pydantic model for extracting pagination query parameters
and a dataclass for wrapping paginated query results.
"""

import math
from dataclasses import dataclass

from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints.

    Attributes:
        page: The 1-based page number to retrieve.
        limit: Maximum number of items per page.
    """

    page: int = 1
    limit: int = 20

    @property
    def offset(self) -> int:
        """Calculate the SQL offset for the current page.

        Returns:
            The zero-based offset for database queries.
        """
        return (self.page - 1) * self.limit


@dataclass
class PaginatedResult:
    """Container for a page of query results with pagination metadata.

    Attributes:
        items: The list of items on the current page.
        total: Total number of items across all pages.
        page: The current page number.
        limit: Maximum items per page.
    """

    items: list
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        """Calculate the total number of pages.

        Returns:
            The total page count, or 0 if there are no items.
        """
        return math.ceil(self.total / self.limit) if self.total > 0 else 0