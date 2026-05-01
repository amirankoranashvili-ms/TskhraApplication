"""Product repository interfaces.

Defines the abstract repository protocols for products and brands,
enabling dependency inversion between core business logic and infrastructure.
"""

from typing import Protocol, Optional, Tuple, List, Dict, Any

from src.app.core.products.entities import Brand, ProductDomainModel, SortByOption
from src.app.core.schemas.product_schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductSlim,
)


class IProductRepository(Protocol):
    """Protocol defining the contract for product persistence operations."""

    async def create_product(
        self, product_data: ProductCreateRequest, is_provider: bool
    ) -> ProductDomainModel:
        """Create a new product.

        Args:
            product_data: The product creation payload.
            is_provider: Whether the creator is a provider (vs. scraper).

        Returns:
            The created product domain model.
        """
        pass

    async def update_product(
        self,
        product_id: int,
        product_data: ProductUpdateRequest,
        is_provider: bool = False,
    ) -> None:
        """Update an existing product.

        Args:
            product_id: The ID of the product to update.
            product_data: The fields to update.
            is_provider: If True, brand_id is an option_id that needs resolving.
        """
        pass

    async def get_by_id(self, product_id: int) -> Optional[ProductDomainModel]:
        """Retrieve a product by its ID.

        Args:
            product_id: The unique product identifier.

        Returns:
            The product domain model, or None if not found.
        """
        pass

    async def search_products(
        self, q: str, limit: int, offset: int, *, in_stock: bool = True
    ) -> Tuple[List[ProductSlim], int]:
        """Search products by text query.

        Args:
            q: The search query string.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            A tuple of (matching products, total count).
        """
        pass

    async def delete_product(self, product_id: int, supplier_id: int) -> None:
        """Soft-delete a product.

        Args:
            product_id: The ID of the product to delete.
            supplier_id: The supplier owning the product.
        """
        pass

    async def reactivate_rejected_product(
        self,
        product_id: int,
        product_data: ProductUpdateRequest,
        is_provider: bool = False,
    ) -> None:
        """Reactivate a previously rejected product with updated data.

        Args:
            product_id: The ID of the product to reactivate.
            product_data: The updated product fields.
            is_provider: If True, brand_id is an option_id that needs resolving.
        """
        pass

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
            sort_by: The sorting strategy.
            dynamic_filters: Additional field-based filters.

        Returns:
            A tuple of (product list, total count).
        """
        pass


class IBrandRepository(Protocol):
    """Protocol defining the contract for brand persistence operations."""

    async def get_by_id(self, brand_id: int) -> Optional[Brand]:
        """Retrieve a brand by its ID.

        Args:
            brand_id: The unique brand identifier.

        Returns:
            The brand entity, or None if not found.
        """
        pass
