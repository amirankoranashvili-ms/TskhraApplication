"""Interactor for creating a new product draft.

Handles the creation of a product upload task in Draft status,
ready for image uploads and submission.
"""

from dataclasses import dataclass
from typing import Any

from src.app.core.products.entities import Status
from src.app.core.products.repository import IProductTaskRepository
from src.app.core.schemas.product_schemas import ProductCreateRequest


@dataclass
class CreateProductCommand:
    """Command object for the create product use case.

    Attributes:
        supplier_id: ID of the seller creating the product.
        product_data: Validated product creation request data.
    """

    supplier_id: int
    product_data: ProductCreateRequest


class CreateProductUseCase:
    """Use case for creating a new product draft task.

    Creates a product upload task in Draft status with an empty
    image list, ready for subsequent image uploads and submission.
    """

    def __init__(self, task_repo: IProductTaskRepository):
        """Initialize the use case with its dependencies.

        Args:
            task_repo: Repository for product upload task persistence.
        """
        self.task_repo = task_repo

    async def execute(self, command: CreateProductCommand) -> dict[str, Any]:
        """Execute the create product use case.

        Args:
            command: Command containing supplier ID and product data.

        Returns:
            Dict with draft status, task ID, and confirmation message.
        """
        payload = command.product_data.model_dump()
        payload["images"] = []
        payload["cover_image_url"] = None

        task = await self.task_repo.create_task(
            supplier_id=command.supplier_id,
            payload=payload,
            status=Status.Draft.value,
        )

        return {
            "status": "DRAFT",
            "task_id": str(task.task_id),
            "message": "Product draft created. Upload images and submit.",
        }
