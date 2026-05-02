"""Port interface for product image storage.

Defines the protocol for saving, deleting, and generating URLs
for product images across different storage backends.
"""

from typing import Protocol


class IImageStorage(Protocol):
    """Port for product image storage operations."""

    async def save_image(self, file_content: bytes, filename: str) -> str:
        """Save an image file and return the generated filename.

        Args:
            file_content: Raw bytes of the image.
            filename: Original filename of the upload.

        Returns:
            The generated storage filename.
        """
        pass

    async def delete_image(self, image_url: str) -> None:
        """Delete an image by its URL.

        Args:
            image_url: URL or path of the image to delete.
        """
        pass

    def generate_image_url(self, filename: str) -> str:
        """Generate a public URL for accessing the image.

        Args:
            filename: The stored filename.

        Returns:
            Public-facing URL string.
        """
        pass
