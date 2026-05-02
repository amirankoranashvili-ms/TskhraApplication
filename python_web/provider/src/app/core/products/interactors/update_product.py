"""Interactor for updating an existing product.

Handles creation of update draft tasks for both resubmission of
rejected products and updates to live catalog products.
"""

from dataclasses import dataclass
from typing import Any

from src.app.core.ports.catalog_client import ICatalogClient
from src.app.core.products.entities import Status
from src.app.core.products.exceptions import (
    DraftAlreadyExistsException,
    VendorProductException,
)
from src.app.core.products.repository import IProductTaskRepository
from src.app.core.schemas.product_schemas import ProductUpdate


@dataclass
class UpdateProductCommand:
    """Command object for the update product use case.

    Attributes:
        supplier_id: ID of the seller updating the product.
        product_id: ID of the product to update.
        product_data: Validated product update request data.
    """

    supplier_id: int
    product_id: int
    product_data: ProductUpdate


class UpdateProductUseCase:
    """Use case for creating a product update draft task.

    Supports both resubmission of rejected products and updates to
    live catalog products. Preserves existing images in the draft.
    """

    def __init__(
        self,
        task_repo: IProductTaskRepository,
        catalog_client: ICatalogClient,
    ):
        """Initialize the use case with its dependencies.

        Args:
            task_repo: Repository for product upload task persistence.
            catalog_client: HTTP client for the catalog service.
        """
        self.task_repo = task_repo
        self.catalog_client = catalog_client

    async def execute(self, command: UpdateProductCommand) -> dict[str, Any]:
        """Execute the update product use case.

        Args:
            command: Command containing supplier ID, product ID, and update data.

        Returns:
            Dict with draft status, task ID, and confirmation message.

        Raises:
            DraftAlreadyExistsException: If a draft already exists for the product.
            VendorProductException: If the product is not found or access is denied.
        """
        existing_draft = await self.task_repo.get_draft_by_product_id(
            command.product_id
        )
        if existing_draft is not None:
            raise DraftAlreadyExistsException()

        existing_task = await self.task_repo.get_task_by_product_id(command.product_id)
        is_resubmission = (
            existing_task is not None and existing_task.status == Status.Rejected
        )

        if is_resubmission:
            if existing_task.supplier_id != command.supplier_id:
                raise VendorProductException(
                    message="Product not found or access denied."
                )

            images = existing_task.payload.get("images", [])
            cover_image_url = existing_task.payload.get("cover_image_url")

            payload = command.product_data.model_dump(exclude_unset=True)
            payload["images"] = images
            payload["cover_image_url"] = cover_image_url
            payload["_original_images"] = images.copy()
            payload["_is_resubmission"] = True

            task = await self.task_repo.create_task(
                supplier_id=command.supplier_id,
                payload=payload,
                status=Status.Draft.value,
                product_id=command.product_id,
            )

            return {
                "status": "DRAFT",
                "task_id": str(task.task_id),
                "message": "Resubmission draft created. Modify images and submit.",
            }

        current_product = await self.catalog_client.get_product_by_id(
            command.product_id
        )
        if current_product is None:
            raise VendorProductException(message="Product not found in catalog.")
        if current_product.get("product", {}).get("supplier_id") != command.supplier_id:
            raise VendorProductException(message="Product not found or access denied.")

        current_images = current_product.get("product", {}).get("images", [])
        current_cover = current_product.get("product", {}).get("image_url")

        payload = command.product_data.model_dump(exclude_unset=True)
        payload["images"] = current_images.copy()
        payload["cover_image_url"] = current_cover
        payload["_original_images"] = current_images.copy()
        payload["_is_resubmission"] = False

        task = await self.task_repo.create_task(
            supplier_id=command.supplier_id,
            payload=payload,
            status=Status.Draft.value,
            product_id=command.product_id,
        )

        return {
            "status": "DRAFT",
            "task_id": str(task.task_id),
            "message": "Product update draft created. Modify images and submit.",
        }
