"""Handle product upload interactor.

Processes product creation messages received from the message broker,
creating new products in the database.
"""

from src.app.core.products.repository import IProductRepository
from src.app.core.schemas.product_schemas import ProductCreateRequest


class HandleProductUploadInteractor:
    """Interactor that handles asynchronous product upload requests."""

    def __init__(self, repository: IProductRepository) -> None:
        """Initialize with a product repository.

        Args:
            repository: The product repository implementation.
        """
        self.repository = repository

    async def execute(self, payload: dict) -> dict:
        """Execute the product upload use case.

        Creates a new product from the payload data.

        Args:
            payload: Dictionary containing product creation data, task_id,
                supplier_id, and optional is_provider flag.

        Returns:
            A result dictionary with task_id, product_id, supplier_id,
            status (SUCCESS/FAILED), and error_message.
        """
        task_id = payload.get("task_id")
        is_provider = payload.get("is_provider", False)
        supplier_id = payload.get("supplier_id")

        try:
            product_req = ProductCreateRequest(**payload)
            created_product = await self.repository.create_product(
                product_req, is_provider
            )
            return {
                "task_id": task_id,
                "product_id": created_product.id,
                "supplier_id": supplier_id,
                "status": "SUCCESS",
                "error_message": None,
            }
        except Exception as e:
            return {
                "task_id": task_id,
                "product_id": None,
                "supplier_id": supplier_id,
                "status": "FAILED",
                "error_message": str(e),
            }
