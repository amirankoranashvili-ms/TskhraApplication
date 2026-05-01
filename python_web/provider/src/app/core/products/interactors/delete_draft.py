"""Use case for deleting a product draft task.

Validates ownership and Draft status before removing the task.
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


@dataclass
class DeleteDraftCommand:
    """Command data for deleting a draft task.

    Attributes:
        supplier_id: ID of the owning seller.
        task_id: UUID of the draft task.
    """

    supplier_id: int
    task_id: UUID


class DeleteDraftUseCase:
    """Deletes a product draft task after validating ownership and status."""

    def __init__(self, task_repo: IProductTaskRepository):
        self.task_repo = task_repo

    async def execute(self, command: DeleteDraftCommand) -> dict[str, Any]:
        """Execute the delete draft use case.

        Args:
            command: Command containing supplier ID and task ID.

        Returns:
            Dict with confirmation message.

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

        await self.task_repo.delete_task(command.task_id)

        return {
            "status": "DELETED",
            "task_id": str(command.task_id),
            "message": "Draft deleted successfully.",
        }
