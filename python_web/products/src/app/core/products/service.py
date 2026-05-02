"""Product and brand service layer.

Contains business logic for retrieving, listing, and searching products
and brands, delegating persistence to repository interfaces.
"""

from typing import Optional, Dict, List, Any, Tuple

from src.app.core.products.exceptions import (
    ProductNotFoundException,
    BrandNotFoundException,
)
from src.app.core.products.entities import (
    Brand,
    ProductDomainModel,
    SortByOption,
)
from src.app.core.products.repository import IProductRepository, IBrandRepository
from src.app.core.schemas.product_schemas import ProductSlim


class ProductService:
    """Service for product-related business operations."""

    def __init__(self, repository: IProductRepository) -> None:
        """Initialize with a product repository.

        Args:
            repository: The product repository implementation.
        """
        self.repository = repository

    async def get_product(self, product_id: int) -> ProductDomainModel:
        """Retrieve a single product by ID.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            The product domain model.

        Raises:
            ProductNotFoundException: If no product exists with the given ID.
        """
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()
        return product

    async def get_products(
        self,
        category_id: Optional[int],
        supplier_id: Optional[int],
        limit: int,
        offset: int,
        min_price: Optional[float],
        max_price: Optional[float],
        sort_by: SortByOption,
        dynamic_filters: Dict[str, List[Any]],
        in_stock: bool = True,
    ) -> Tuple[List[ProductSlim], int]:
        """Retrieve a filtered and sorted list of products.

        Args:
            category_id: Optional category filter.
            supplier_id: Optional supplier filter.
            limit: Maximum number of products to return.
            offset: Number of products to skip.
            min_price: Optional minimum price filter.
            max_price: Optional maximum price filter.
            sort_by: Sorting strategy to apply.
            dynamic_filters: Additional field-based filters as key-value lists.

        Returns:
            A tuple of (product list, total count).
        """
        return await self.repository.get_products(
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

    async def search_products(
        self, q: str, limit: int, offset: int
    ) -> Tuple[List[ProductSlim], int]:
        """Search products by text query using the database fallback.

        Args:
            q: The search query string.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            A tuple of (matching products, total count).
        """
        return await self.repository.search_products(q, limit, offset)


class BrandService:
    """Service for brand-related business operations."""

    def __init__(self, repository: IBrandRepository):
        """Initialize with a brand repository.

        Args:
            repository: The brand repository implementation.
        """
        self.repository = repository

    async def get_brand_by_id(self, brand_id: int) -> Brand:
        """Retrieve a brand by its ID.

        Args:
            brand_id: The unique identifier of the brand.

        Returns:
            The brand entity.

        Raises:
            BrandNotFoundException: If no brand exists with the given ID.
        """
        brand = await self.repository.get_by_id(brand_id)
        if not brand:
            raise BrandNotFoundException()
        return brand
