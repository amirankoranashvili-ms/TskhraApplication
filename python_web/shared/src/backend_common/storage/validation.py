"""File upload validation utilities.

Provides helpers to detect MIME types and validate uploaded files against
allowed types and size limits.
"""

import asyncio

import magic
from fastapi import UploadFile

from backend_common.exceptions import ValidationException

ALLOWED_IMAGE_TYPES: set[str] = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/heic",
}

MIME_TO_EXT: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/gif": ".gif",
}

MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB


async def detect_mime_type(content: bytes) -> str:
    """Detect the MIME type of file content using libmagic.

    Args:
        content: The raw file bytes (only the first 2048 bytes are examined).

    Returns:
        The detected MIME type string (e.g. ``image/png``).
    """
    header = content[:2048]
    return await asyncio.to_thread(magic.from_buffer, header, mime=True)


async def validate_image(
    content: bytes,
    allowed_types: set[str] | None = None,
    max_size: int | None = None,
) -> str:
    """Validate image content against size and type constraints.

    Args:
        content: The raw image bytes.
        allowed_types: Set of acceptable MIME types. Defaults to
            ``ALLOWED_IMAGE_TYPES``.
        max_size: Maximum file size in bytes. Defaults to ``MAX_IMAGE_SIZE``.

    Returns:
        The detected MIME type of the valid image.

    Raises:
        ValidationException: If the file exceeds the size limit or has
            a disallowed MIME type.
    """
    limit = max_size or MAX_IMAGE_SIZE
    if len(content) > limit:
        raise ValidationException(
            f"File size exceeds {limit // (1024 * 1024)}MB limit"
        )

    mime_type = await detect_mime_type(content)
    allowed = allowed_types or ALLOWED_IMAGE_TYPES
    if mime_type not in allowed:
        raise ValidationException(f"Invalid file type: {mime_type}")

    return mime_type


async def validate_upload_file(
    file: UploadFile,
    allowed_types: set[str] | None = None,
    max_size: int | None = None,
) -> tuple[bytes, str]:
    """Validate a single FastAPI upload file.

    Reads the file content, validates it, and resets the file cursor.

    Args:
        file: The FastAPI ``UploadFile`` to validate.
        allowed_types: Set of acceptable MIME types.
        max_size: Maximum file size in bytes.

    Returns:
        A tuple of (file content bytes, detected MIME type).

    Raises:
        ValidationException: If the file fails validation.
    """
    content = await file.read()
    await file.seek(0)
    mime_type = await validate_image(content, allowed_types, max_size)
    return content, mime_type


async def validate_upload_files(
    files: list[UploadFile],
    max_files: int = 10,
    allowed_types: set[str] | None = None,
    max_size: int | None = None,
) -> None:
    """Validate a list of FastAPI upload files.

    Args:
        files: List of ``UploadFile`` objects to validate.
        max_files: Maximum number of files allowed.
        allowed_types: Set of acceptable MIME types.
        max_size: Maximum size per file in bytes.

    Raises:
        ValidationException: If no valid files are provided, too many
            files are given, or any file fails validation.
    """
    valid_files = [f for f in files if f.filename]

    if not valid_files:
        raise ValidationException("No valid files provided")

    if len(valid_files) > max_files:
        raise ValidationException(f"Too many files. Maximum: {max_files}")

    for file in valid_files:
        header = await file.read(2048)
        await file.seek(0)

        limit = max_size or MAX_IMAGE_SIZE
        if file.size is not None and file.size > limit:
            raise ValidationException(
                f"File size exceeds {limit // (1024 * 1024)}MB limit"
            )

        mime_type = await detect_mime_type(header)
        allowed = allowed_types or ALLOWED_IMAGE_TYPES
        if mime_type not in allowed:
            raise ValidationException(f"Invalid file type: {mime_type}")


def get_extension(mime_type: str) -> str:
    """Get the file extension for a MIME type.

    Args:
        mime_type: The MIME type string.

    Returns:
        The corresponding file extension (e.g. ``.jpg``), defaulting
        to ``.jpg`` for unknown types.
    """
    return MIME_TO_EXT.get(mime_type, ".jpg")