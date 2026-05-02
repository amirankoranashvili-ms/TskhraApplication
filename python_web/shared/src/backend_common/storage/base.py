"""Abstract file storage protocol definition.

Defines the interface that all storage backends (MinIO, local filesystem, etc.)
must implement for saving and deleting files.
"""

from typing import Protocol


class IFileStorage(Protocol):
    """Protocol defining the file storage interface.

    All storage implementations must provide ``save`` and ``delete`` methods
    with these signatures.
    """

    async def save(self, content: bytes, filename: str, content_type: str = "") -> str:
        """Save file content and return its public URL or path.

        Args:
            content: The raw file bytes.
            filename: The original filename (used for extension detection).
            content_type: Optional MIME type; auto-detected if empty.

        Returns:
            The URL or path where the file can be accessed.
        """
        ...

    async def delete(self, path: str) -> None:
        """Delete a file by its URL or path.

        Args:
            path: The URL or path returned by ``save``.
        """
        ...