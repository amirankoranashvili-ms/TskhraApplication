"""Product domain model mappers.

Provides functions to convert rich ProductDomainModel instances into
flattened response models such as Product and ProductSlim.
"""

from collections import defaultdict

from src.app.core.products.entities import (
    Product,
    ProductDomainModel,
    Specification,
    ProductSpecification,
)
from src.app.core.schemas.product_schemas import ProductSlim


def map_domain_to_product(product_domain: ProductDomainModel) -> Product:
    """Map a ProductDomainModel to a full Product response model.

    Groups field values into specification groups and resolves the cover image.

    Args:
        product_domain: The rich domain model with all relationships loaded.

    Returns:
        A flat Product model suitable for API responses.
    """
    image_url_strings = [img.image_url for img in product_domain.images]

    if product_domain.cover_image_url:
        cover_url = product_domain.cover_image_url
    elif image_url_strings:
        cover_url = image_url_strings[0]
    else:
        cover_url = ""

    grouped_specs = defaultdict(list)
    for fv in product_domain.field_values:
        if fv.option and fv.option.field:
            group_name = (
                fv.option.field.group.name if fv.option.field.group else "Ungrouped"
            )
            grouped_specs[group_name].append(
                Specification(name=fv.option.field.name, value=fv.option.value)
            )

    specifications = [
        ProductSpecification(group_name=g_name, specifications=specs)
        for g_name, specs in grouped_specs.items()
    ]

    return Product(
        id=product_domain.id,
        category_id=product_domain.category_id,
        supplier_id=product_domain.supplier_id,
        brand=product_domain.brand,
        title=product_domain.title,
        description=product_domain.description or "",
        price=product_domain.price,
        sku=product_domain.sku,
        stock_quantity=product_domain.stock_quantity,
        image_url=cover_url,
        images=image_url_strings,
        specifications=specifications,
        category=product_domain.category,
    )


def map_domain_to_slim(product_domain: ProductDomainModel) -> ProductSlim:
    """Map a ProductDomainModel to a slim product summary.

    Resolves the cover image from cover_image_url or the first gallery image.

    Args:
        product_domain: The rich domain model to convert.

    Returns:
        A lightweight ProductSlim model for list/search views.
    """
    image_url_strings = [img.image_url for img in product_domain.images]
    if product_domain.cover_image_url:
        cover_url = product_domain.cover_image_url
    elif image_url_strings:
        cover_url = image_url_strings[0]
    else:
        cover_url = ""

    return ProductSlim(
        id=product_domain.id,
        brand=product_domain.brand,
        price=product_domain.price,
        title=product_domain.title,
        description=product_domain.description,
        cover_image_url=cover_url,
        stock_quantity=product_domain.stock_quantity,
        sku=product_domain.sku,
        images=image_url_strings,
    )
