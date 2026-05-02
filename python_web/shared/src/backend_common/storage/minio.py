"""MinIO/S3-compatible object storage backend.

Implements the ``IFileStorage`` interface by saving and deleting objects
in a MinIO bucket, with automatic bucket creation and public read policy.
"""

import io
import json
import uuid
from pathlib import PurePosixPath

from miniopy_async import Minio

from backend_common.storage.base import IFileStorage
from backend_common.storage.validation import MIME_TO_EXT, detect_mime_type


class MinioFileStorage(IFileStorage):
    """File storage implementation backed by MinIO (S3-compatible object storage)."""
    def __init__(self, client: Minio, bucket: str, public_url: str | None = None) -> None:
        """Initialize the MinIO file storage.

        Args:
            client: An async MinIO client instance.
            bucket: The bucket name to store objects in.
            public_url: Optional public base URL for constructing object URLs.
        """
        self._client = client
        self._bucket = bucket
        self._public_url = public_url
        self._bucket_ready = False

    async def _ensure_bucket(self) -> None:
        """Ensure the target bucket exists with a public read policy.

        Creates the bucket if it does not exist and applies a policy
        granting public read access to all objects.
        """
        if self._bucket_ready:
            return
        if not await self._client.bucket_exists(self._bucket):
            await self._client.make_bucket(self._bucket)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self._bucket}/*"],
                }
            ],
        }
        await self._client.set_bucket_policy(self._bucket, json.dumps(policy))
        self._bucket_ready = True

    async def save(self, content: bytes, filename: str, content_type: str = "") -> str:
        """Save file content to MinIO.

        Args:
            content: The raw file bytes.
            filename: The original filename (used for extension fallback).
            content_type: MIME type of the file. Detected automatically if empty.

        Returns:
            The URL or path to the saved object.
        """
        await self._ensure_bucket()

        if not content_type:
            content_type = await detect_mime_type(content)

        ext = MIME_TO_EXT.get(content_type, PurePosixPath(filename).suffix or ".bin")
        key = f"{uuid.uuid4().hex}{ext}"

        stream = io.BytesIO(content)
        await self._client.put_object(
            self._bucket, key, stream, length=len(content), content_type=content_type
        )

        if self._public_url:
            return f"{self._public_url}/{self._bucket}/{key}"
        return f"{self._bucket}/{key}"

    async def delete(self, path: str) -> None:
        """Delete an object from MinIO.

        Args:
            path: The object path or URL. The object key is extracted
                from the last path segment.
        """
        key = path.rstrip("/").split("/")[-1]
        await self._client.remove_object(self._bucket, key)