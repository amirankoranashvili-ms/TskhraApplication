"""Image upload utilities: validation, saving, and deletion."""

import asyncio
import uuid

import aiofiles
from backend_common.storage.validation import MIME_TO_EXT, detect_mime_type
from starlette.datastructures import UploadFile

from src.app.core.config import settings

ALLOWED_MIME_TYPES: frozenset[str] = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
    }
)

UPLOAD_SUBDIRS: dict[str, str] = {
    "avatars": "avatars",
    "listing_photos": "listing_photos",
    "products": "products",
    "categories": "categories",
    "brands": "brands",
}


class UploadValidationError(Exception):
    """Raised when an uploaded file fails validation checks."""

    def __init__(self, message: str) -> None:
        """Initialise with a human-readable error message.

        Args:
            message: Description of the validation failure.
        """
        self.message = message
        super().__init__(message)


async def validate_image(content: bytes) -> str:
    """Validate uploaded image content for size and MIME type.

    Args:
        content: Raw bytes of the uploaded file.

    Returns:
        The detected MIME type string.

    Raises:
        UploadValidationError: If the file is empty, too large, or has a
            disallowed MIME type.
    """
    if len(content) == 0:
        raise UploadValidationError("File is empty.")

    if len(content) > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE // (1024 * 1024)
        raise UploadValidationError(f"File too large. Maximum size is {max_mb} MB.")

    mime_type = await detect_mime_type(content)

    if mime_type not in ALLOWED_MIME_TYPES:
        raise UploadValidationError(
            f"Invalid file type: {mime_type}. "
            f"Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
        )

    return mime_type


async def save_upload(upload_file: UploadFile, entity_type: str) -> str:
    """Validate and persist an uploaded image to disk.

    Args:
        upload_file: The Starlette UploadFile instance.
        entity_type: Key from UPLOAD_SUBDIRS indicating the target subdirectory.

    Returns:
        The URL path to the saved file (e.g. ``/uploads/products/abc.jpg``).

    Raises:
        ValueError: If entity_type is not recognised.
        UploadValidationError: If the file fails validation.
    """
    if entity_type not in UPLOAD_SUBDIRS:
        raise ValueError(f"Unknown entity type: {entity_type}")

    content = await upload_file.read()
    mime_type = await validate_image(content)
    extension = MIME_TO_EXT.get(mime_type, ".jpg")

    subdir = UPLOAD_SUBDIRS[entity_type]
    target_dir = settings.UPLOAD_DIR / subdir
    await asyncio.to_thread(target_dir.mkdir, parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = target_dir / filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return f"/uploads/{subdir}/{filename}"


async def delete_upload(url_path: str) -> None:
    """Delete a previously uploaded file from disk.

    Silently ignores paths that do not start with ``/uploads/`` or that
    resolve outside the configured upload directory.

    Args:
        url_path: The URL path of the file to delete.
    """
    if not url_path or not url_path.startswith("/uploads/"):
        return

    relative = url_path.removeprefix("/uploads/")
    file_path = settings.UPLOAD_DIR / relative

    resolved = file_path.resolve()
    if not str(resolved).startswith(str(settings.UPLOAD_DIR.resolve())):
        return

    if await asyncio.to_thread(file_path.exists):
        await asyncio.to_thread(file_path.unlink, True)


def is_upload_file_with_content(value: object) -> bool:
    """Check whether a value is an UploadFile with a non-empty filename.

    Args:
        value: The object to inspect.

    Returns:
        True if value is an UploadFile with a truthy filename.
    """
    if not isinstance(value, UploadFile):
        return False
    if not value.filename:
        return False
    return True
