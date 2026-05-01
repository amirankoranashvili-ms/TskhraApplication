"""Local filesystem image storage implementation.

Stores product images on the local filesystem with MIME type detection
and URL generation via FastAPI request routing.
"""

import asyncio
import uuid

import magic
from fastapi import Request

from src.app.core.config import settings
from src.app.core.ports.image_storage import IImageStorage

MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
}


class LocalImageStorage(IImageStorage):
    """Image storage implementation using the local filesystem."""

    def __init__(self, request: Request):
        """Initialize with a FastAPI request for URL generation.

        Args:
            request: The current FastAPI request object.
        """
        self.request = request

    async def save_image(self, file_content: bytes, filename: str) -> str:
        """Save an image to the local filesystem.

        Args:
            file_content: Raw image bytes.
            filename: Original filename (used for MIME detection fallback).

        Returns:
            The generated filename with UUID and detected extension.
        """
        await asyncio.to_thread(
            settings.PRODUCT_IMAGES_DIR.mkdir, parents=True, exist_ok=True
        )

        mime_type = await asyncio.to_thread(
            magic.from_buffer, file_content[:2048], mime=True
        )
        ext = MIME_TO_EXT.get(mime_type, "jpg")
        new_filename = f"{uuid.uuid4()}.{ext}"
        filepath = settings.PRODUCT_IMAGES_DIR / new_filename

        await asyncio.to_thread(filepath.write_bytes, file_content)

        return new_filename

    async def delete_image(self, image_url: str) -> None:
        """Delete an image from the local filesystem.

        Args:
            image_url: URL of the image; filename is extracted from the last path segment.
        """
        filename = image_url.rstrip("/").split("/")[-1]
        filepath = (settings.PRODUCT_IMAGES_DIR / filename).resolve()
        if not filepath.is_relative_to(settings.PRODUCT_IMAGES_DIR.resolve()):
            return
        if await asyncio.to_thread(filepath.exists):
            await asyncio.to_thread(filepath.unlink)

    def generate_image_url(self, filename: str) -> str:
        """Generate a public URL for the image using FastAPI routing.

        Args:
            filename: The stored filename.

        Returns:
            Full URL string for the image endpoint.
        """
        return str(self.request.url_for("get_product_image", filename=filename))
