"""Unit tests for image upload validation and helpers."""

from unittest.mock import AsyncMock, patch

import pytest
from starlette.datastructures import UploadFile

from src.app.infra.web.upload import (
    UploadValidationError,
    is_upload_file_with_content,
    validate_image,
)


@pytest.mark.asyncio
class TestValidateImage:
    async def test_empty_file_raises(self):
        with pytest.raises(UploadValidationError, match="empty"):
            await validate_image(b"")

    async def test_oversized_file_raises(self):
        with patch("src.app.infra.web.upload.settings") as mock_settings:
            mock_settings.MAX_UPLOAD_SIZE = 100
            with pytest.raises(UploadValidationError, match="too large"):
                await validate_image(b"x" * 101)

    async def test_invalid_mime_raises(self):
        with (
            patch("src.app.infra.web.upload.settings") as mock_settings,
            patch(
                "src.app.infra.web.upload.detect_mime_type", new_callable=AsyncMock
            ) as mock_detect,
        ):
            mock_settings.MAX_UPLOAD_SIZE = 10_000
            mock_detect.return_value = "application/pdf"

            with pytest.raises(UploadValidationError, match="Invalid file type"):
                await validate_image(b"fake-content")

    async def test_valid_jpeg_returns_mime(self):
        with (
            patch("src.app.infra.web.upload.settings") as mock_settings,
            patch(
                "src.app.infra.web.upload.detect_mime_type", new_callable=AsyncMock
            ) as mock_detect,
        ):
            mock_settings.MAX_UPLOAD_SIZE = 10_000
            mock_detect.return_value = "image/jpeg"

            result = await validate_image(b"fake-jpeg")
            assert result == "image/jpeg"

    async def test_valid_webp_returns_mime(self):
        with (
            patch("src.app.infra.web.upload.settings") as mock_settings,
            patch(
                "src.app.infra.web.upload.detect_mime_type", new_callable=AsyncMock
            ) as mock_detect,
        ):
            mock_settings.MAX_UPLOAD_SIZE = 10_000
            mock_detect.return_value = "image/webp"

            result = await validate_image(b"fake-webp")
            assert result == "image/webp"


class TestIsUploadFileWithContent:
    def _make_upload(self, filename):
        import io

        return UploadFile(file=io.BytesIO(b""), filename=filename)

    def test_valid_upload_file(self):
        assert is_upload_file_with_content(self._make_upload("photo.jpg")) is True

    def test_upload_file_empty_filename(self):
        assert is_upload_file_with_content(self._make_upload("")) is False

    def test_upload_file_none_filename(self):
        assert is_upload_file_with_content(self._make_upload(None)) is False

    def test_not_upload_file(self):
        assert is_upload_file_with_content("not-a-file") is False

    def test_none(self):
        assert is_upload_file_with_content(None) is False
