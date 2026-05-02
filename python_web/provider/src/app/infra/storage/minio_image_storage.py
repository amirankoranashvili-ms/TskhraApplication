"""MinIO-based image storage implementation.

Adapts the shared MinioFileStorage to the IImageStorage port interface
for storing product images in MinIO object storage.
"""

from backend_common.storage import MinioFileStorage

from src.app.core.ports.image_storage import IImageStorage


class MinioImageStorage(IImageStorage):
    """Image storage implementation backed by MinIO object storage."""

    def __init__(self, storage: MinioFileStorage) -> None:
        """Initialize with a MinIO file storage instance.

        Args:
            storage: Configured MinioFileStorage backend.
        """
        self._storage = storage

    async def save_image(self, file_content: bytes, filename: str) -> str:
        """Save an image to MinIO storage.

        Args:
            file_content: Raw image bytes.
            filename: Original filename.

        Returns:
            The generated storage filename.
        """
        return await self._storage.save(file_content, filename)

    async def delete_image(self, image_url: str) -> None:
        """Delete an image from MinIO storage.

        Args:
            image_url: URL or path of the image to delete.
        """
        await self._storage.delete(image_url)

    def generate_image_url(self, filename: str) -> str:
        """Generate a URL for the stored image.

        Args:
            filename: The stored filename.

        Returns:
            The filename as-is (URL construction handled by MinIO).
        """
        return filename
