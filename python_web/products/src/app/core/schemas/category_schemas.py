"""Category API schemas.

Pydantic models for category-related API responses, including
category listings, filter configurations, and categories with products.
"""

from typing import List, Optional

from pydantic import BaseModel

from src.app.core.categories.entities import Category
from src.app.core.schemas.product_schemas import ProductSlim


class FieldOptionsOut(BaseModel):
    """Output schema for a single selectable field option."""

    option_id: int
    option_value: str
    product_count: int = 0


class FilterFieldOut(BaseModel):
    """Output schema for a filter field with its available options."""

    field_id: int
    field_name: str
    is_required: bool
    options: List[FieldOptionsOut]


class CategoryFilterOut(BaseModel):
    """Output schema for a group of filter fields."""

    group_id: Optional[int] = None
    group_name: str
    fields: List[FilterFieldOut]


class BrandFilterOut(BaseModel):
    """Output schema for a brand with product count."""

    brand_id: int
    brand_name: str
    logo_url: Optional[str] = None
    product_count: int = 0


class GetCategoryFiltersResponse(BaseModel):
    """Response schema containing all filter groups for a category."""

    filters: List[CategoryFilterOut]
    brands: List[BrandFilterOut] = []


class GetAllCategoriesResponse(BaseModel):
    """Response schema containing a list of categories."""

    categories: List[Category]


class CategoryWithProducts(Category):
    """Category extended with a list of slim product summaries."""

    products: List[ProductSlim] = []


class GetCategoriesWithProductsResponse(BaseModel):
    """Response schema containing categories with their products."""

    categories: List[CategoryWithProducts]
