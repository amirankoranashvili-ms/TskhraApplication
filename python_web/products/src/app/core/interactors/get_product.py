"""Get product interactor.

Retrieves a single product by ID and maps it to the API response format.
"""

from src.app.core.products.mappers import map_domain_to_product
from src.app.core.products.service import ProductService
from src.app.core.schemas.product_schemas import GetProductResponse


class GetProductInteractor:
    """Interactor that retrieves a single product with full details."""

    def __init__(self, product_service: ProductService) -> None:
        """Initialize with a product service.

        Args:
            product_service: Service for product operations.
        """
        self.product_service = product_service

    async def execute(self, product_id: int) -> GetProductResponse:
        """Execute the get-product use case.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            Response containing the full product details.
        """
        product_domain = await self.product_service.get_product(product_id)
        product = map_domain_to_product(product_domain)
        return GetProductResponse(product=product)
