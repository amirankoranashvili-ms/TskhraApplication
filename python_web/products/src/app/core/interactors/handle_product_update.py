"""Handle product update interactor.

Processes product update messages received from the message broker,
applying updates or reactivating rejected products.
"""

from src.app.core.products.repository import IProductRepository
from src.app.core.schemas.product_schemas import ProductUpdateRequest


class HandleProductUpdateInteractor:
    """Interactor that handles asynchronous product update requests."""

    def __init__(self, repository: IProductRepository) -> None:
        """Initialize with a product repository.

        Args:
            repository: The product repository implementation.
        """
        self.repository = repository

    async def execute(self, payload: dict) -> dict:
        """Execute the product update use case.

        Applies the update or reactivates a rejected product based on the
        is_resubmission flag in the payload.

        Args:
            payload: Dictionary containing product update data, task_id,
                product_id, and optional is_resubmission flag.

        Returns:
            A result dictionary with task_id, product_id, supplier_id,
            status (SUCCESS/FAILED), and error_message.
        """
        task_id = payload.get("task_id")
        product_id = payload.get("product_id")
        is_resubmission = payload.get("is_resubmission", False)
        is_provider = payload.get("is_provider", False)

        try:
            update_req = ProductUpdateRequest(**payload)
            if is_resubmission:
                await self.repository.reactivate_rejected_product(
                    product_id, update_req, is_provider
                )
            else:
                await self.repository.update_product(
                    product_id, update_req, is_provider
                )

            return {
                "task_id": task_id,
                "product_id": product_id,
                "supplier_id": payload.get("supplier_id"),
                "status": "SUCCESS",
                "error_message": None,
            }
        except Exception as e:
            return {
                "task_id": task_id,
                "product_id": product_id,
                "supplier_id": payload.get("supplier_id"),
                "status": "FAILED",
                "error_message": str(e),
            }
