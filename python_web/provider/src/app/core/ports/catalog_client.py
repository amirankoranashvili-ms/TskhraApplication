"""Port interface for the catalog service HTTP client.

Defines the protocol for communicating with the external products/catalog
service to retrieve product and supplier data.
"""

from typing import Any, Protocol


class ICatalogClient(Protocol):
    """Port for communicating with the main catalog service."""

    async def get_product_by_id(self, product_id: int) -> dict[str, Any] | None:
        """Get a product by its ID from the catalog.

        Args:
            product_id: The product identifier.

        Returns:
            Product data dict, or None if not found or unreachable.
        """
        pass

    async def get_supplier_ids_for_products(
        self, product_ids: list[int]
    ) -> dict[int, int]:
        """Get supplier ID mapping for a batch of product IDs.

        Args:
            product_ids: List of product IDs to look up.

        Returns:
            Dict mapping product_id to supplier_id.
        """
        pass

    async def get_vendor_products(
        self, supplier_id: int, page: int, limit: int
    ) -> dict[str, Any] | None:
        """Get a vendor's products from the catalog with pagination.

        Args:
            supplier_id: ID of the vendor.
            page: Page number.
            limit: Items per page.

        Returns:
            Paginated product data dict, or None if unreachable.
        """
        pass
