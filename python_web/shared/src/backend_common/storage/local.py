"""Local filesystem storage backend.

Implements the ``IFileStorage`` interface by saving and deleting files
on the local filesystem under a configurable base directory.
"""

import asyncio
import uuid
from pathlib import Path

from backend_common.storage.base import IFileStorage
from backend_common.storage.validation import MIME_TO_EXT, detect_mime_type


class LocalFileStorage(IFileStorage):
    """File storage implementation that persists files to the local filesystem."""
    def __init__(self, base_dir: Path, url_prefix: str = "/uploads") -> None:
        """Initialize the local file storage.

        Args:
            base_dir: The directory where files will be stored.
            url_prefix: URL prefix for constructing file URLs.
        """
        self.base_dir = base_dir
        self.url_prefix = url_prefix.rstrip("/")

    async def save(self, content: bytes, filename: str, content_type: str = "") -> str:
        """Save file content to the local filesystem.

        Args:
            content: The raw file bytes.
            filename: The original filename (used for extension fallback).
            content_type: MIME type of the file. Detected automatically if empty.

        Returns:
            The URL path to the saved file.
        """
        await asyncio.to_thread(self.base_dir.mkdir, parents=True, exist_ok=True)

        if not content_type:
            content_type = await detect_mime_type(content)

        ext = MIME_TO_EXT.get(content_type, Path(filename).suffix or ".bin")
        new_filename = f"{uuid.uuid4().hex}{ext}"
        filepath = self.base_dir / new_filename

        await asyncio.to_thread(filepath.write_bytes, content)
        return f"{self.url_prefix}/{new_filename}"

    async def delete(self, path: str) -> None:
        """Delete a file from the local filesystem.

        Performs a path traversal check to ensure the file is within
        the base directory. Silently ignores files that do not exist
        or paths outside the base directory.

        Args:
            path: The URL path or filename of the file to delete.
        """
        filename = path.rstrip("/").split("/")[-1]
        filepath = (self.base_dir / filename).resolve()

        if not filepath.is_relative_to(self.base_dir.resolve()):
            return

        if await asyncio.to_thread(filepath.exists):
            await asyncio.to_thread(filepath.unlink)