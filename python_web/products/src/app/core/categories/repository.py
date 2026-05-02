"""Category repository interfaces.

Defines abstract repository protocols for categories and category fields,
enabling dependency inversion between core logic and infrastructure.
"""

from typing import Protocol, List, Optional

from src.app.core.categories.entities import (
    Category,
    CategoryFieldDomainModel,
    CategoryWithProductsDomainModel,
)


class ICategoryRepository(Protocol):
    """Protocol defining the contract for category persistence operations."""

    async def get_all(self, parent_id: Optional[int] = None) -> List[Category]:
        """Retrieve all categories, optionally filtered by parent.

        Args:
            parent_id: If provided, return only children of this parent.

        Returns:
            A list of category entities.
        """
        pass

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Retrieve a single category by its ID.

        Args:
            category_id: The unique category identifier.

        Returns:
            The category entity, or None if not found.
        """
        pass

    async def get_categories_with_top_products(
        self,
        limit_per_cat: int,
        parent_id: Optional[int] = None,
    ) -> List[CategoryWithProductsDomainModel]:
        """Retrieve categories with their top N products.

        Args:
            limit_per_cat: Maximum number of products per category.
            parent_id: If provided, filter by parent category.

        Returns:
            A list of categories with embedded product lists.
        """
        pass


class ICategoryFieldRepository(Protocol):
    """Protocol for category field and option lookups."""

    async def get_fields_and_options_for_category(
        self, category_id: int
    ) -> List[CategoryFieldDomainModel]:
        """Retrieve all fields and their options for a category.

        Args:
            category_id: The category to fetch fields for.

        Returns:
            A list of category field domain models with nested options.
        """
        pass
