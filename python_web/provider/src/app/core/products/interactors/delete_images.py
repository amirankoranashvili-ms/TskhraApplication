"""Use case for deleting images from a product draft task.

Removes specified images from the draft payload and deletes newly uploaded
images from storage (preserving original images for update drafts).
"""

import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.app.core.ports.image_storage import IImageStorage
from src.app.core.products.entities import Status
from src.app.core.products.exceptions import (
    ImageNotInDraftException,
    TaskNotDraftException,
    TaskNotFoundException,
    VendorProductException,
)
from src.app.core.products.repository import IProductTaskRepository


@dataclass
class DeleteImagesCommand:
    """Command data for deleting images from a draft task.

    Attributes:
        supplier_id: ID of the owning seller.
        task_id: UUID of the draft task.
        image_urls: List of image URLs to remove.
    """

    supplier_id: int
    task_id: UUID
    image_urls: list[str]


class DeleteImagesUseCase:
    """Deletes images from a product draft task and cleans up storage."""

    def __init__(
        self,
        task_repo: IProductTaskRepository,
        image_storage: IImageStorage,
    ):
        """Initialize the use case.

        Args:
            task_repo: Product task repository.
            image_storage: Image storage implementation.
        """
        self.task_repo = task_repo
        self.image_storage = image_storage

    async def execute(self, command: DeleteImagesCommand) -> dict[str, Any]:
        """Execute the delete images use case.

        Args:
            command: Command containing task ID and image URLs to delete.

        Returns:
            Dict with task status, remaining images, and cover image URL.

        Raises:
            TaskNotFoundException: If the task does not exist.
            VendorProductException: If access is denied.
            TaskNotDraftException: If the task is not in Draft status.
            ImageNotInDraftException: If any image URL is not in the draft.
        """
        task = await self.task_repo.get_task(command.task_id)
        if task is None:
            raise TaskNotFoundException()
        if task.supplier_id != command.supplier_id:
            raise VendorProductException(message="Task not found or access denied.")
        if task.status != Status.Draft:
            raise TaskNotDraftException()

        current_images = task.payload.get("images", [])
        original_images = set(task.payload.get("_original_images", []))

        for url in command.image_urls:
            if url not in current_images:
                raise ImageNotInDraftException()

        new_uploads_to_delete = [
            url for url in command.image_urls if url not in original_images
        ]
        if new_uploads_to_delete:
            await asyncio.gather(
                *(self.image_storage.delete_image(url) for url in new_uploads_to_delete)
            )

        remaining_images = [
            img for img in current_images if img not in command.image_urls
        ]

        payload = task.payload.copy()
        payload["images"] = remaining_images

        current_cover = payload.get("cover_image_url")
        if current_cover in command.image_urls:
            payload["cover_image_url"] = (
                remaining_images[0] if remaining_images else None
            )

        await self.task_repo.update_task_payload(command.task_id, payload)

        return {
            "status": "DRAFT",
            "task_id": str(command.task_id),
            "images": payload["images"],
            "cover_image_url": payload["cover_image_url"],
        }
