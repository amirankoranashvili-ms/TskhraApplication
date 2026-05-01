"""Mixin and formatters for image upload handling in SQLAdmin views."""

from __future__ import annotations

from typing import Any, ClassVar, Type

from markupsafe import Markup
from sqladmin.fields import FileField
from starlette.requests import Request
from wtforms import Form

from src.app.infra.web.upload import (
    UploadValidationError,
    delete_upload,
    is_upload_file_with_content,
    save_upload,
)


def image_preview_formatter(url_attr: str):
    """Create a column formatter that renders a small image thumbnail.

    Args:
        url_attr: Name of the model attribute containing the image URL.

    Returns:
        A formatter callable suitable for SQLAdmin column_formatters.
    """

    def _formatter(model: Any, name: str) -> Markup:
        url = getattr(model, url_attr, None)
        if not url:
            return Markup('<span class="text-muted">—</span>')
        return Markup(
            '<img src="{}" style="max-height:40px;max-width:80px;'
            'object-fit:contain;border-radius:4px;" loading="lazy" />'
        ).format(url)

    return _formatter


def image_detail_formatter(url_attr: str):
    """Create a column formatter that renders a larger image for the detail view.

    Args:
        url_attr: Name of the model attribute containing the image URL.

    Returns:
        A formatter callable suitable for SQLAdmin column_formatters_detail.
    """

    def _formatter(model: Any, name: str) -> Markup:
        url = getattr(model, url_attr, None)
        if not url:
            return Markup('<span class="text-muted">—</span>')
        return Markup(
            '<img src="{}" style="max-height:200px;max-width:300px;'
            'object-fit:contain;border-radius:8px;" loading="lazy" />'
        ).format(url)

    return _formatter


class ImageUploadMixin:
    """Mixin for SQLAdmin ModelViews that need image upload support.

    Subclasses should define ``_upload_fields`` as a dict mapping form field
    names to ``(url_column, entity_type)`` tuples.
    """

    _upload_fields: ClassVar[dict[str, tuple[str, str]]] = {}

    async def scaffold_form(self, rules: list[str] | None = None) -> Type[Form]:
        """Extend the auto-generated form with FileField entries for uploads.

        Args:
            rules: Optional list of form field rules.

        Returns:
            The augmented WTForms form class.
        """
        form_class = await super().scaffold_form(rules)

        for field_name, (url_column, _) in self._upload_fields.items():
            label = url_column.replace("_", " ").title().replace("Url", "").strip()
            setattr(form_class, field_name, FileField(label=label))

        return form_class

    async def on_model_change(
        self, data: dict, model: Any, is_created: bool, request: Request
    ) -> None:
        """Handle file uploads when a model is created or updated.

        Args:
            data: The form data dictionary (mutated in place).
            model: The SQLAlchemy model instance being modified.
            is_created: True if the model is being created, False if updated.
            request: The incoming HTTP request.

        Raises:
            ValueError: If validation fails or a required image is missing.
        """
        for field_name, (url_column, entity_type) in self._upload_fields.items():
            upload_value = data.pop(field_name, None)

            if is_upload_file_with_content(upload_value):
                try:
                    if not is_created:
                        old_url = getattr(model, url_column, None)
                        if old_url:
                            await delete_upload(old_url)

                    new_url = await save_upload(upload_value, entity_type)
                    data[url_column] = new_url
                except UploadValidationError as e:
                    raise ValueError(str(e)) from e
            elif not is_created:
                existing_url = getattr(model, url_column, None)
                if existing_url:
                    data[url_column] = existing_url
            else:
                col = getattr(self.model, url_column).property.columns[0]
                if not col.nullable:
                    raise ValueError("Image upload is required.")

        await super().on_model_change(data, model, is_created, request)

    async def on_model_delete(self, model: Any, request: Request) -> None:
        """Delete associated uploaded files when a model is removed.

        Args:
            model: The SQLAlchemy model instance being deleted.
            request: The incoming HTTP request.
        """
        for _, (url_column, _) in self._upload_fields.items():
            url = getattr(model, url_column, None)
            if url:
                await delete_upload(url)

        await super().on_model_delete(model, request)
