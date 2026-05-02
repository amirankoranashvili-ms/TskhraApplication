"""Interactor for uploading images to a product draft task.

Handles concurrent image saving and updates the task payload with
the new image URLs, enforcing a maximum image count.
"""

import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.app.core.ports.image_storage import IImageStorage
from src.app.core.products.entities import Status
from src.app.core.products.exceptions import (
    TaskNotDraftException,
    TaskNotFoundException,
    TooManyImagesException,
    VendorProductException,
)
from src.app.core.products.repository import IProductTaskRepository

MAX_PRODUCT_IMAGES = 5


@dataclass
class ImageFile:
    """Represents an uploaded image file.

    Attributes:
        content: Raw bytes of the image file.
        filename: Original filename of the upload.
    """

    content: bytes
    filename: str


@dataclass
class UploadImagesCommand:
    """Command object for the upload images use case.

    Attributes:
        supplier_id: ID of the seller uploading images.
        task_id: UUID of the draft task to attach images to.
        image_files: List of image files to upload.
    """

    supplier_id: int
    task_id: UUID
    image_files: list[ImageFile]


class UploadImagesUseCase:
    """Use case for uploading images to a product draft task.

    Saves images concurrently to storage, appends URLs to the task
    payload, and sets the cover image if not already set.
    """

    def __init__(
        self,
        task_repo: IProductTaskRepository,
        image_storage: IImageStorage,
    ):
        """Initialize the use case with its dependencies.

        Args:
            task_repo: Repository for product upload task persistence.
            image_storage: Storage backend for product images.
        """
        self.task_repo = task_repo
        self.image_storage = image_storage

    async def _save_image(self, image_file: ImageFile) -> str:
        """Save a single image file to storage and return its URL.

        Args:
            image_file: The image file to save.

        Returns:
            Public URL of the saved image.
        """
        filename = await self.image_storage.save_image(
            image_file.content, image_file.filename
        )
        return self.image_storage.generate_image_url(filename)

    async def execute(self, command: UploadImagesCommand) -> dict[str, Any]:
        """Execute the upload images use case.

        Args:
            command: Command containing supplier ID, task ID, and image files.

        Returns:
            Dict with draft status, task ID, image URLs, and cover image URL.

        Raises:
            TaskNotFoundException: If the task does not exist.
            VendorProductException: If the task does not belong to the supplier.
            TaskNotDraftException: If the task is not in Draft status.
            TooManyImagesException: If adding images exceeds the maximum.
        """
        task = await self.task_repo.get_task(command.task_id)
        if task is None:
            raise TaskNotFoundException()
        if task.supplier_id != command.supplier_id:
            raise VendorProductException(message="Task not found or access denied.")
        if task.status != Status.Draft:
            raise TaskNotDraftException()

        current_images = task.payload.get("images", [])
        if len(current_images) + len(command.image_files) > MAX_PRODUCT_IMAGES:
            raise TooManyImagesException(max_images=MAX_PRODUCT_IMAGES)

        saved_urls = list(
            await asyncio.gather(*(self._save_image(f) for f in command.image_files))
        )

        payload = task.payload.copy()
        payload["images"] = current_images + saved_urls
        if not payload.get("cover_image_url"):
            payload["cover_image_url"] = payload["images"][0]

        await self.task_repo.update_task_payload(command.task_id, payload)

        return {
            "status": "DRAFT",
            "task_id": str(command.task_id),
            "images": payload["images"],
            "cover_image_url": payload["cover_image_url"],
        }
