"""List products interactor.

Retrieves a paginated, filtered, and sorted list of products.
"""

import math
from typing import Any, Optional

from src.app.core.products.entities import SortByOption
from src.app.core.products.service import ProductService
from src.app.core.schemas.product_schemas import ProductSearchResponse


class ListProductsInteractor:
    """Interactor that lists products with pagination, filtering, and sorting.

    Attributes:
        product_service: The domain service used to query products.
    """

    def __init__(self, product_service: ProductService) -> None:
        """Initialise the interactor.

        Args:
            product_service: Domain service for product operations.
        """
        self.product_service = product_service

    async def execute(
        self,
        category_id: Optional[int],
        supplier_id: Optional[int],
        page: int,
        limit: int,
        min_price: Optional[float],
        max_price: Optional[float],
        sort_by: SortByOption,
        dynamic_filters: dict[str, list[Any]],
        in_stock: bool = True,
    ) -> ProductSearchResponse:
        """Execute the list-products use case.

        Args:
            category_id: Optional category filter.
            supplier_id: Optional supplier filter.
            page: The page number (1-based).
            limit: Maximum number of items per page.
            min_price: Optional minimum price filter.
            max_price: Optional maximum price filter.
            sort_by: The sorting strategy to apply.
            dynamic_filters: Additional field-based filters as key-value lists.

        Returns:
            A paginated response containing matching products and metadata.
        """
        offset = (page - 1) * limit

        products, total_count = await self.product_service.get_products(
            category_id=category_id,
            supplier_id=supplier_id,
            limit=limit,
            offset=offset,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            dynamic_filters=dynamic_filters,
            in_stock=in_stock,
        )

        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0

        return ProductSearchResponse(
            items=products,
            total=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )
