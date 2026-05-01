"""Get filters interactor.

Retrieves the available filter options for a given product category,
with product counts reflecting the currently applied filters.
"""

from typing import Optional

from src.app.core.categories.service import CategoryService
from src.app.core.schemas.category_schemas import GetCategoryFiltersResponse


class GetFiltersInteractor:
    """Interactor that retrieves category filter configuration."""

    def __init__(self, category_service: CategoryService) -> None:
        """Initialize with a category service.

        Args:
            category_service: Service for category operations.
        """
        self.category_service = category_service

    async def execute(
        self,
        category_id: int,
        brand_ids: Optional[list[int]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: bool = True,
        applied_option_ids: Optional[list[int]] = None,
    ) -> GetCategoryFiltersResponse:
        """Execute the get-filters use case.

        Args:
            category_id: The category to retrieve filters for.
            brand_ids: Currently selected brand IDs.
            min_price: Current minimum price filter.
            max_price: Current maximum price filter.
            in_stock: Whether to count only in-stock products.
            applied_option_ids: Currently selected option IDs.

        Returns:
            Response containing grouped filter fields and options with counts.
        """
        return await self.category_service.get_filters(
            category_id=category_id,
            brand_ids=brand_ids,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            applied_option_ids=applied_option_ids,
        )
