"""SQLAdmin views for product-related models (categories, brands, products, fields, sellers, verification)."""

import logging

from markupsafe import Markup, escape
from sqladmin import ModelView, action
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.app.core.constants import SessionKeys, VerificationStatus
from src.app.core.verification_service import VerificationService
from src.app.infra.database.engines import vendor_engine
from src.app.infra.database.models.products import (
    BrandDb,
    CategoryDb,
    CategoryFieldDb,
    FieldDb,
    FieldGroupDb,
    FieldOptionDb,
    PlatformSellerDb,
    ProductDb,
    ProductFieldValueDb,
    ProductImageDb,
    SupplierDb,
    VerificationRequestDb,
)
from src.app.infra.database.session import async_session
from src.app.infra.web.views._soft_delete_mixin import SoftDeleteMixin
from src.app.infra.web.views._upload_mixin import (
    ImageUploadMixin,
    image_detail_formatter,
    image_preview_formatter,
)

logger = logging.getLogger(__name__)


class CategoryAdmin(SoftDeleteMixin, ImageUploadMixin, ModelView, model=CategoryDb):
    """Admin view for managing product categories with cascade soft-delete."""

    name = "Category"
    name_plural = "Categories"
    icon = "fa-solid fa-folder-tree"

    _cascade_soft_delete_models = [
        (ProductDb, ProductDb.category_id),
    ]

    _upload_fields = {
        "image_upload": ("image_url", "categories"),
    }

    column_list = [
        CategoryDb.id,
        CategoryDb.name,
        CategoryDb.slug,
        CategoryDb.image_url,
        CategoryDb.parent_id,
        CategoryDb.is_deleted,
        CategoryDb.created_at,
    ]
    column_searchable_list = [CategoryDb.name, CategoryDb.slug]
    column_sortable_list = [CategoryDb.name, CategoryDb.created_at]
    column_default_sort = ("id", False)

    form_excluded_columns = [CategoryDb.created_at, CategoryDb.image_url]

    column_formatters = {
        CategoryDb.image_url: image_preview_formatter("image_url"),
    }
    column_formatters_detail = {
        CategoryDb.image_url: image_detail_formatter("image_url"),
    }


class BrandAdmin(SoftDeleteMixin, ImageUploadMixin, ModelView, model=BrandDb):
    """Admin view for managing brands with cascade soft-delete."""

    name = "Brand"
    name_plural = "Brands"
    icon = "fa-solid fa-tag"

    _cascade_soft_delete_models = [
        (ProductDb, ProductDb.brand_id),
    ]

    _upload_fields = {
        "logo_upload": ("logo_url", "brands"),
    }

    column_list = [
        BrandDb.id,
        BrandDb.name,
        BrandDb.logo_url,
        BrandDb.is_deleted,
        BrandDb.created_at,
    ]
    column_searchable_list = [BrandDb.name]
    column_sortable_list = [BrandDb.name, BrandDb.created_at]
    column_default_sort = ("id", False)

    form_excluded_columns = [BrandDb.created_at, BrandDb.logo_url]

    column_formatters = {
        BrandDb.logo_url: image_preview_formatter("logo_url"),
    }
    column_formatters_detail = {
        BrandDb.logo_url: image_detail_formatter("logo_url"),
    }


class SupplierAdmin(SoftDeleteMixin, ModelView, model=SupplierDb):
    """Admin view for managing suppliers with cascade soft-delete."""

    name = "Supplier"
    name_plural = "Suppliers"
    icon = "fa-solid fa-truck"

    _cascade_soft_delete_models = [
        (ProductDb, ProductDb.supplier_id),
        (PlatformSellerDb, PlatformSellerDb.supplier_id, {"is_active": False}),
    ]

    column_list = [
        SupplierDb.id,
        SupplierDb.name,
        SupplierDb.supplier_type,
        SupplierDb.is_deleted,
        SupplierDb.created_at,
    ]
    column_searchable_list = [SupplierDb.name]
    column_sortable_list = [SupplierDb.name, SupplierDb.created_at]
    column_default_sort = ("id", False)

    form_excluded_columns = [SupplierDb.created_at]


def _product_images_detail_formatter(model, name):
    """Format product images as an HTML gallery for the detail view.

    Args:
        model: The ProductDb model instance.
        name: The column name being formatted.

    Returns:
        Markup containing image tags or a placeholder.
    """
    images = model.images or []
    if not images:
        return Markup('<span class="text-muted">No images</span>')
    html_parts = []
    for img in images:
        if img.image_url:
            html_parts.append(
                Markup(
                    '<img src="{}" style="max-height:200px;max-width:300px;'
                    'object-fit:contain;border-radius:8px;margin:4px;" '
                    'loading="lazy" />'
                ).format(img.image_url)
            )
    return (
        Markup(
            '<div style="display:flex;flex-wrap:wrap;gap:8px;">'
            + "".join(html_parts)
            + "</div>"
        )
        if html_parts
        else Markup('<span class="text-muted">No images</span>')
    )


def _product_field_values_detail_formatter(model, name):
    """Format product field values as an HTML list for the detail view.

    Args:
        model: The ProductDb model instance.
        name: The column name being formatted.

    Returns:
        Markup containing a list of field-value pairs or a placeholder.
    """
    field_values = model.field_values or []
    if not field_values:
        return Markup('<span class="text-muted">—</span>')
    items = []
    for fv in field_values:
        field_name = fv.field.name if fv.field else f"Field #{fv.field_id}"
        option_value = fv.option.value if fv.option else f"Option #{fv.option_id}"
        items.append(
            Markup("<li><strong>{}</strong>: {}</li>").format(
                escape(field_name), escape(option_value)
            )
        )
    return Markup("<ul style='margin:0;padding-left:20px;'>" + "".join(items) + "</ul>")


class ProductAdmin(SoftDeleteMixin, ImageUploadMixin, ModelView, model=ProductDb):
    """Admin view for managing products with cover image upload and soft-delete."""

    name = "Product"
    name_plural = "Products"
    icon = "fa-solid fa-box"

    column_select_related_list = ["category", "supplier", "brand"]

    _upload_fields = {
        "cover_image_upload": ("cover_image_url", "products"),
    }

    column_list = [
        ProductDb.id,
        ProductDb.title,
        ProductDb.cover_image_url,
        ProductDb.sku,
        ProductDb.price,
        ProductDb.stock_quantity,
        ProductDb.is_active,
        ProductDb.is_deleted,
        ProductDb.created_at,
    ]
    column_details_list = [
        ProductDb.id,
        ProductDb.title,
        ProductDb.description,
        ProductDb.cover_image_url,
        "images",
        ProductDb.sku,
        ProductDb.price,
        ProductDb.cost_price,
        ProductDb.stock_quantity,
        ProductDb.original_url,
        ProductDb.sell_type,
        "category",
        "supplier",
        "brand",
        "field_values",
        ProductDb.is_active,
        ProductDb.is_deleted,
        ProductDb.created_at,
        ProductDb.updated_at,
    ]
    column_labels = {
        "images": "Images",
        "category": "Category",
        "supplier": "Supplier",
        "brand": "Brand",
        "field_values": "Field Values",
    }
    column_searchable_list = [ProductDb.title, ProductDb.sku]
    column_sortable_list = [
        ProductDb.title,
        ProductDb.price,
        ProductDb.stock_quantity,
        ProductDb.created_at,
        ProductDb.is_active,
    ]
    column_default_sort = ("created_at", True)

    form_excluded_columns = [
        ProductDb.created_at,
        ProductDb.updated_at,
        ProductDb.cover_image_url,
    ]

    column_formatters = {
        ProductDb.cover_image_url: image_preview_formatter("cover_image_url"),
    }
    column_formatters_detail = {
        ProductDb.cover_image_url: image_detail_formatter("cover_image_url"),
        "images": _product_images_detail_formatter,
        "field_values": _product_field_values_detail_formatter,
    }

    @action(
        name="approve_verification",
        label="Verify",
        confirmation_message="Approve verification for this product?",
        add_in_list=False,
        add_in_detail=True,
    )
    async def action_approve_verification(self, request: Request):

        pks = request.query_params.get("pks", "")
        if not pks:
            return RedirectResponse(
                request.url_for("admin:list", identity=self.identity), status_code=302
            )

        product_id = int(pks)
        admin_username = request.session.get(SessionKeys.USERNAME, "unknown")

        vendor_factory = async_sessionmaker(
            vendor_engine, class_=AsyncSession, expire_on_commit=False
        )

        try:
            publisher = None
            try:
                from src.app.infra.broker.connection import publisher
            except Exception:
                pass

            async with (
                async_session() as products_session,
                vendor_factory() as vendor_session,
            ):
                result = await products_session.execute(
                    select(VerificationRequestDb.id)
                    .where(
                        VerificationRequestDb.product_id == product_id,
                        VerificationRequestDb.status
                        == VerificationStatus.PENDING.value,
                    )
                    .order_by(VerificationRequestDb.id.desc())
                    .limit(1)
                )
                vr_id = result.scalar_one_or_none()
                if vr_id:
                    service = VerificationService(
                        products_session, vendor_session, publisher
                    )
                    await service.approve(vr_id, admin_username)
        except Exception:
            logger.exception(
                "Failed to approve verification for product %s", product_id
            )

        referer = request.headers.get("referer")
        if referer:
            return RedirectResponse(referer, status_code=302)
        return RedirectResponse(
            request.url_for("admin:list", identity=self.identity), status_code=302
        )


class ProductImageAdmin(ImageUploadMixin, ModelView, model=ProductImageDb):
    """Admin view for managing individual product images."""

    name = "Product Image"
    name_plural = "Product Images"
    icon = "fa-solid fa-images"

    _upload_fields = {
        "image_upload": ("image_url", "products"),
    }

    column_list = [
        ProductImageDb.id,
        ProductImageDb.product_id,
        ProductImageDb.image_url,
        ProductImageDb.created_at,
    ]

    form_excluded_columns = [ProductImageDb.created_at, ProductImageDb.image_url]

    column_formatters = {
        ProductImageDb.image_url: image_preview_formatter("image_url"),
    }
    column_formatters_detail = {
        ProductImageDb.image_url: image_detail_formatter("image_url"),
    }


class FieldGroupAdmin(ModelView, model=FieldGroupDb):
    """Admin view for managing field groups."""

    name = "Field Group"
    name_plural = "Field Groups"
    icon = "fa-solid fa-layer-group"

    column_list = [FieldGroupDb.id, FieldGroupDb.name]
    column_searchable_list = [FieldGroupDb.name]


class FieldAdmin(ModelView, model=FieldDb):
    """Admin view for managing product specification fields."""

    name = "Field"
    name_plural = "Fields"
    icon = "fa-solid fa-font"

    column_list = [FieldDb.id, FieldDb.name, FieldDb.group_id]
    column_searchable_list = [FieldDb.name]


class FieldOptionAdmin(ModelView, model=FieldOptionDb):
    """Admin view for managing selectable field options."""

    name = "Field Option"
    name_plural = "Field Options"
    icon = "fa-solid fa-list-check"

    column_list = [
        FieldOptionDb.id,
        FieldOptionDb.field_id,
        FieldOptionDb.value,
    ]
    column_searchable_list = [FieldOptionDb.value]


class CategoryFieldAdmin(ModelView, model=CategoryFieldDb):
    """Admin view for managing category-field associations."""

    name = "Category Field"
    name_plural = "Category Fields"
    icon = "fa-solid fa-link"

    column_list = [
        CategoryFieldDb.id,
        CategoryFieldDb.category_id,
        CategoryFieldDb.field_id,
        CategoryFieldDb.is_required,
    ]


class ProductFieldValueAdmin(ModelView, model=ProductFieldValueDb):
    """Admin view for managing product field values."""

    name = "Product Field Value"
    name_plural = "Product Field Values"
    icon = "fa-solid fa-pen-to-square"

    column_list = [
        ProductFieldValueDb.id,
        ProductFieldValueDb.product_id,
        ProductFieldValueDb.field_id,
        ProductFieldValueDb.option_id,
    ]


class PlatformSellerAdmin(ModelView, model=PlatformSellerDb):
    """Read-only admin view for platform sellers."""

    name = "Platform Seller"
    name_plural = "Platform Sellers"
    icon = "fa-solid fa-store"

    column_list = [
        PlatformSellerDb.supplier_id,
        PlatformSellerDb.user_id,
        PlatformSellerDb.identification_number,
        PlatformSellerDb.legal_address,
        PlatformSellerDb.contact_phone,
        PlatformSellerDb.contact_email,
        PlatformSellerDb.is_active,
    ]
    column_searchable_list = [
        PlatformSellerDb.identification_number,
        PlatformSellerDb.contact_email,
    ]
    column_sortable_list = [PlatformSellerDb.supplier_id, PlatformSellerDb.is_active]
    column_default_sort = ("supplier_id", False)

    can_create = False
    can_edit = False
    can_delete = False


def _actions_formatter(model, name):
    """Format the status column with approve/reject action buttons for pending requests.

    Args:
        model: The VerificationRequestDb model instance.
        name: The column name being formatted.

    Returns:
        Markup with action buttons if pending, otherwise the plain status string.
    """
    if model.status == VerificationStatus.PENDING.value:
        return Markup(
            '<a href="/verification/{}/approve" '
            'class="btn btn-sm btn-success me-1" '
            "onclick=\"return confirm('Approve this request?')\">Approve</a>"
            '<a href="/verification/{}/reject" '
            'class="btn btn-sm btn-danger">Reject</a>'
        ).format(model.id, model.id)
    return model.status


def _supplier_name_formatter(model, name):
    """Format the supplier column to show the supplier name and ID.

    Args:
        model: The VerificationRequestDb model instance.
        name: The column name being formatted.

    Returns:
        A string with the supplier name and ID, or the raw supplier_id.
    """
    if model.supplier:
        return f"{model.supplier.name} (#{model.supplier_id})"
    return model.supplier_id or ""


def _product_title_formatter(model, name):
    """Format the product column to show the product title and ID.

    Args:
        model: The VerificationRequestDb model instance.
        name: The column name being formatted.

    Returns:
        A string with the product title and ID, or the raw product_id.
    """
    if model.product:
        return f"{model.product.title} (#{model.product_id})"
    return model.product_id or ""


class VerificationRequestAdmin(ModelView, model=VerificationRequestDb):
    """Read-only admin view for verification requests with inline approve/reject actions."""

    name = "Verification Request"
    name_plural = "Verification Requests"
    icon = "fa-solid fa-clipboard-check"

    column_select_related_list = ["supplier", "product"]

    column_list = [
        VerificationRequestDb.id,
        VerificationRequestDb.request_type,
        VerificationRequestDb.status,
        "supplier",
        "product",
        VerificationRequestDb.rejection_reason,
        VerificationRequestDb.created_at,
        VerificationRequestDb.resolved_at,
    ]
    column_labels = {
        "supplier": "Supplier",
        "product": "Product",
    }
    column_searchable_list = [
        VerificationRequestDb.request_type,
        VerificationRequestDb.status,
    ]
    column_sortable_list = [
        VerificationRequestDb.id,
        VerificationRequestDb.request_type,
        VerificationRequestDb.created_at,
        VerificationRequestDb.status,
    ]
    column_default_sort = ("id", True)

    can_create = False
    can_edit = False
    can_delete = False

    column_formatters = {
        VerificationRequestDb.status: _actions_formatter,
        "supplier": _supplier_name_formatter,
        "product": _product_title_formatter,
    }
