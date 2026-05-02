"""Use case for updating product data in an existing draft task.

Merges new product fields into the existing draft payload without
affecting images or other metadata.
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.app.core.products.entities import Status
from src.app.core.products.exceptions import (
    TaskNotDraftException,
    TaskNotFoundException,
    VendorProductException,
)
from src.app.core.products.repository import IProductTaskRepository
from src.app.core.schemas.product_schemas import ProductUpdate


@dataclass
class UpdateDraftCommand:
    """Command data for updating a draft task's product fields.

    Attributes:
        supplier_id: ID of the owning seller.
        task_id: UUID of the draft task.
        product_data: Partial product update fields.
    """

    supplier_id: int
    task_id: UUID
    product_data: ProductUpdate


class UpdateDraftUseCase:
    """Updates product data fields within an existing draft task."""

    def __init__(self, task_repo: IProductTaskRepository):
        """Initialize the use case.

        Args:
            task_repo: Product task repository.
        """
        self.task_repo = task_repo

    async def execute(self, command: UpdateDraftCommand) -> dict[str, Any]:
        """Execute the update draft use case.

        Args:
            command: Command containing task ID and updated product data.

        Returns:
            Dict with draft status, task_id, and confirmation message.

        Raises:
            TaskNotFoundException: If the task does not exist.
            VendorProductException: If access is denied.
            TaskNotDraftException: If the task is not in Draft status.
        """
        task = await self.task_repo.get_task(command.task_id)
        if task is None:
            raise TaskNotFoundException()
        if task.supplier_id != command.supplier_id:
            raise VendorProductException(message="Task not found or access denied.")
        if task.status != Status.Draft:
            raise TaskNotDraftException()

        payload = task.payload.copy()
        updates = command.product_data.model_dump(exclude_unset=True)
        payload.update(updates)

        await self.task_repo.update_task_payload(command.task_id, payload)

        return {
            "status": "DRAFT",
            "task_id": str(command.task_id),
            "message": "Draft updated successfully.",
        }
