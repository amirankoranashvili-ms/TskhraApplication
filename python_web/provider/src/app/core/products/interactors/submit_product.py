"""Use case for submitting a product draft for review.

Validates the draft has images, publishes creation or update events
to the message broker, and transitions the task to Pending status.
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic import ValidationError

from src.app.core.ports.event_publisher import IEventPublisher
from src.app.core.products.entities import Status
from src.app.core.products.exceptions import (
    InvalidDraftDataException,
    NoImagesException,
    TaskNotDraftException,
    TaskNotFoundException,
    VendorProductException,
)
from src.app.core.products.repository import IProductTaskRepository
from src.app.core.schemas.product_schemas import ProductCreateRequest


@dataclass
class SubmitProductCommand:
    """Command data for submitting a product draft.

    Attributes:
        supplier_id: ID of the owning seller.
        task_id: UUID of the draft task to submit.
    """

    supplier_id: int
    task_id: UUID


class SubmitProductUseCase:
    """Submits a product draft for review by publishing domain events."""

    def __init__(
        self,
        task_repo: IProductTaskRepository,
        publisher: IEventPublisher,
    ):
        """Initialize the use case.

        Args:
            task_repo: Product task repository.
            publisher: Event publisher for domain events.
        """
        self.task_repo = task_repo
        self.publisher = publisher

    async def execute(self, command: SubmitProductCommand) -> dict[str, Any]:
        """Execute the submit product use case.

        Args:
            command: Command containing supplier ID and task ID.

        Returns:
            Dict with pending status, task_id, and confirmation message.

        Raises:
            TaskNotFoundException: If the task does not exist.
            VendorProductException: If access is denied.
            TaskNotDraftException: If the task is not in Draft status.
            NoImagesException: If the draft has no images.
        """
        task = await self.task_repo.get_task(command.task_id)
        if task is None:
            raise TaskNotFoundException()
        if task.supplier_id != command.supplier_id:
            raise VendorProductException(message="Task not found or access denied.")
        if task.status != Status.Draft:
            raise TaskNotDraftException()

        images = task.payload.get("images", [])
        if len(images) < 1:
            raise NoImagesException()

        try:
            ProductCreateRequest(
                **{k: v for k, v in task.payload.items() if not k.startswith("_")}
            )
        except ValidationError as e:
            raise InvalidDraftDataException(errors=e.errors())

        await self.task_repo.update_task_status(command.task_id, Status.Pending.value)

        is_update = task.product_id is not None

        if is_update:
            original_images = set(task.payload.get("_original_images", []))
            current_images = set(images)

            new_images = list(current_images - original_images)
            deleted_images = list(original_images - current_images)

            event_payload = {
                k: v for k, v in task.payload.items() if not k.startswith("_")
            }
            event_payload["supplier_id"] = command.supplier_id
            event_payload["product_id"] = task.product_id
            event_payload["task_id"] = str(command.task_id)
            event_payload["is_provider"] = True
            event_payload["new_images"] = new_images
            event_payload["deleted_images"] = deleted_images

            if task.payload.get("_is_resubmission"):
                event_payload["is_resubmission"] = True

            await self.publisher.publish_product_updated(event_payload)
        else:
            event_payload = {
                k: v for k, v in task.payload.items() if not k.startswith("_")
            }
            event_payload["supplier_id"] = command.supplier_id
            event_payload["task_id"] = str(command.task_id)
            event_payload["is_provider"] = True

            await self.publisher.publish_product_created(event_payload)

        clean_payload = {k: v for k, v in task.payload.items() if not k.startswith("_")}
        await self.task_repo.update_task_payload(command.task_id, clean_payload)

        return {
            "status": "PENDING",
            "task_id": str(command.task_id),
            "message": "Product submitted for review.",
        }
