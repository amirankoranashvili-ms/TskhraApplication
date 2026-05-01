"""Category domain exceptions.

Custom exception raised when a category entity cannot be found.
"""

from backend_common.exceptions import EntityNotFoundException


class CategoryNotFoundException(EntityNotFoundException):
    """Raised when a requested category does not exist."""

    message = "Category not found."
