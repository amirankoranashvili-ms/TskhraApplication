"""Abstract repository interface for product upload task persistence.

Defines the protocol that all product task repository implementations must follow.
"""

from typing import Protocol
from uuid import UUID

from src.app.core.products.entities import ProductUploadTask, Status


class IProductTaskRepository(Protocol):
    """Repository protocol for managing product upload tasks.

    Implementations must provide async methods for CRUD operations
    on product upload task data.
    """

    async def create_task(
        self,
        supplier_id: int,
        payload: dict,
        status: str = Status.Pending.value,
        error_message: str | None = None,
        product_id: int | None = None,
    ) -> ProductUploadTask:
        """Create a new product upload task.

        Args:
            supplier_id: ID of the owning seller.
            payload: Product data as a JSON-serializable dict.
            status: Initial task status.
            error_message: Optional error message.
            product_id: Optional associated product ID.

        Returns:
            The created task entity.
        """
        pass

    async def get_task(self, task_id: UUID) -> ProductUploadTask | None:
        """Get a task by its unique ID.

        Args:
            task_id: UUID of the task.

        Returns:
            The task entity, or None if not found.
        """
        pass

    async def update_task_payload(self, task_id: UUID, payload: dict) -> None:
        """Update the payload JSON of an existing task.

        Args:
            task_id: UUID of the task to update.
            payload: New payload data.
        """
        pass

    async def get_draft_by_product_id(
        self, product_id: int
    ) -> ProductUploadTask | None:
        """Get a Draft-status task for a given product ID.

        Args:
            product_id: The product identifier.

        Returns:
            The draft task, or None if not found.
        """
        pass

    async def get_tasks_by_supplier(
        self, supplier_id: int, statuses: list[str]
    ) -> list[ProductUploadTask]:
        """Get all tasks for a supplier filtered by statuses.

        Args:
            supplier_id: ID of the seller.
            statuses: List of status values to filter by.

        Returns:
            List of matching task entities.
        """
        pass

    async def update_task_status(
        self,
        task_id: UUID,
        status: str,
        error_message: str | None = None,
        product_id: int | None = None,
    ) -> None:
        """Update task status and optionally set error message or product ID.

        Args:
            task_id: UUID of the task.
            status: New status value.
            error_message: Optional error description.
            product_id: Optional product ID to associate.
        """
        pass

    async def delete_task(self, task_id: UUID) -> None:
        """Delete a task by its ID.

        Args:
            task_id: UUID of the task to delete.
        """
        pass

    async def reject_task_by_product_id(
        self, product_id: int, error_message: str
    ) -> None:
        """Reject the task associated with a product ID.

        Args:
            product_id: The product identifier.
            error_message: Rejection reason.
        """
        pass

    async def get_task_by_product_id(self, product_id: int) -> ProductUploadTask | None:
        """Get the task associated with a product ID.

        Args:
            product_id: The product identifier.

        Returns:
            The matching task, or None if not found.
        """
        pass
