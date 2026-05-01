import math
from typing import Any, Optional

from src.app.core.products.service import ProductService
from src.app.core.schemas.product_schemas import ProductSearchResponse

SORT_MAP = {
    "price_asc": ["price:asc"],
    "price_desc": ["price:desc"],
    "newest": ["created_at:desc"],
}


class SearchProductsInteractor:
    def __init__(
        self,
        product_service: ProductService,
        search_repository,
    ) -> None:
        self.product_service = product_service
        self.search_repository = search_repository

    async def execute(
        self,
        q: str,
        page: int,
        limit: int,
        *,
        in_stock: bool = True,
        category_id: Optional[int] = None,
        brand_ids: Optional[list[int]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = None,
        spec_filters: Optional[dict[str, list[Any]]] = None,
    ) -> ProductSearchResponse:
        """Execute the search-products use case.

        Args:
            q: The search query string.
            page: The page number (1-based).
            limit: Maximum number of items per page.
            in_stock: If true, only return products with stock_quantity > 0.
            category_id: Optional category filter.
            brand_ids: Optional brand IDs filter.
            min_price: Optional minimum price filter.
            max_price: Optional maximum price filter.
            sort_by: Optional sort strategy name (price_asc, price_desc, newest).
            spec_filters: Optional specification field filters.

        Returns:
            A paginated response containing matching products and metadata.
        """
        offset = (page - 1) * limit

        if self.search_repository:
            sort = SORT_MAP.get(sort_by) if sort_by else None
            products, total_count = await self.search_repository.search_products(
                q,
                limit,
                offset,
                in_stock=in_stock,
                category_id=category_id,
                brand_ids=brand_ids,
                min_price=min_price,
                max_price=max_price,
                sort=sort,
                spec_filters=spec_filters,
            )
        else:
            products, total_count = await self.product_service.search_products(
                q, limit, offset
            )

        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0

        return ProductSearchResponse(
            items=products,
            total=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )
