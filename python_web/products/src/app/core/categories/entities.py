"""Category domain entities and value objects.

Defines the core domain models for categories, category fields, field options,
and their relationships used by the products service.
"""

from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from src.app.core.products.entities import ProductDomainModel, Brand

# ==========================================
# FLAT MODELS (For Basic CRUD)
# ==========================================


class Category(BaseModel):
    """Flat category entity for listing and basic CRUD operations."""

    id: int
    parent_id: Optional[int] = None
    name: str
    slug: str
    image_url: Optional[str] = None
    has_subcategories: bool = False
    product_count: int = 0

    brands: List[Brand] = []

    model_config = ConfigDict(from_attributes=True)


class CategoryFieldGroup(BaseModel):
    """Group that organizes related category fields together."""

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CategoryField(BaseModel):
    """A specification field associated with a category."""

    id: int
    category_id: int
    group_id: Optional[int] = None
    name: str
    is_required: bool

    model_config = ConfigDict(from_attributes=True)


class CategoryFieldOptions(BaseModel):
    """A selectable option for a category field."""

    id: int
    field_id: int
    value: str

    model_config = ConfigDict(from_attributes=True)


class CategoryFieldValue(BaseModel):
    """A selected field option value for a specific product."""

    id: int
    product_id: int
    field_id: int
    option_id: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# NESTED DOMAIN MODELS (Needed for the Filter Feature)
# ==========================================


class FieldOptionDomainModel(BaseModel):
    """Domain model for a selectable field option with its value."""

    id: int
    field_id: int
    value: str
    model_config = ConfigDict(from_attributes=True)


class FieldGroupDomainModel(BaseModel):
    """Domain model for a field group used in category filters."""

    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class FieldDomainModel(BaseModel):
    """Domain model for a specification field with its group."""

    id: int
    name: str
    group_id: Optional[int] = None
    group: Optional[FieldGroupDomainModel] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryFieldDomainModel(BaseModel):
    """Domain model for a field assigned to a category, with its options."""

    id: int
    category_id: int
    field_id: int
    is_required: bool
    field: FieldDomainModel
    option: Optional[FieldOptionDomainModel] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryDomainModel(BaseModel):
    """Domain model for a category with recursive subcategories."""

    id: int
    parent_id: Optional[int] = None
    name: str
    slug: str
    image_url: Optional[str] = None
    subcategories: Optional[List["CategoryDomainModel"]] = []

    model_config = ConfigDict(from_attributes=True)


class CategoryWithProductsDomainModel(Category):
    """Category domain model enriched with a list of products."""

    products: List[ProductDomainModel] = []
    model_config = ConfigDict(from_attributes=True)
