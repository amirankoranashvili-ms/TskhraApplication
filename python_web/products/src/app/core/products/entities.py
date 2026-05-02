"""Product domain entities and value objects.

Defines the core domain models for products, brands, specifications,
and categories used throughout the products service business logic.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SortByOption(str, Enum):
    """Enumeration of available product sorting strategies."""

    POPULAR = "popular"
    NEWEST = "newest"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"


# ==========================================
# FLAT MODELS (For Basic CRUD)
# ==========================================
class Brand(BaseModel):
    """Brand entity representing a product manufacturer or label."""

    id: int
    name: str
    logo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Specification(BaseModel):
    """A single specification key-value pair for a product."""

    name: str
    value: str

    model_config = ConfigDict(from_attributes=True)


class ProductSpecification(BaseModel):
    """A group of related specifications for a product."""

    group_name: str
    specifications: List[Specification] = []

    model_config = ConfigDict(from_attributes=True)


class ParentCategory(BaseModel):
    """Lightweight representation of a parent category."""

    id: int
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


class ProductCategory(BaseModel):
    """Category assigned to a product, with optional parent reference."""

    id: int
    name: str
    slug: str
    parent: Optional[ParentCategory] = None

    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    """Full product entity used for detailed product views."""

    id: int
    category_id: int
    supplier_id: int
    brand: Brand
    image_url: str
    title: str
    description: str
    price: float
    sku: str
    stock_quantity: int
    images: List[str] = []
    specifications: List[ProductSpecification] = []
    category: Optional[ProductCategory] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# NESTED DOMAIN MODELS (Needed for the Filter Feature)
# ==========================================
class FieldGroupDomainModel(BaseModel):
    """Domain model for a group of specification fields."""

    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class FieldDomainModel(BaseModel):
    """Domain model for a specification field with its group."""

    id: int
    name: str
    group: Optional[FieldGroupDomainModel] = None
    model_config = ConfigDict(from_attributes=True)


class FieldOptionDomainModel(BaseModel):
    """Domain model for a selectable option within a specification field."""

    id: int
    value: str
    field: FieldDomainModel
    model_config = ConfigDict(from_attributes=True)


class ProductFieldValueDomainModel(BaseModel):
    """Domain model linking a product to a chosen field option."""

    id: int
    option: Optional[FieldOptionDomainModel] = None
    model_config = ConfigDict(from_attributes=True)


class ProductImageDomainModel(BaseModel):
    """Domain model for a product image reference."""

    id: int
    image_url: str
    model_config = ConfigDict(from_attributes=True)


class ProductDomainModel(BaseModel):
    """Rich domain model for a product with all nested relationships."""

    id: int
    category_id: int
    supplier_id: int
    title: str
    description: Optional[str] = None
    price: float
    sku: str
    stock_quantity: int = 0
    cover_image_url: Optional[str] = None
    brand: Brand
    images: List[ProductImageDomainModel] = []
    field_values: List[ProductFieldValueDomainModel] = []
    category: Optional[ProductCategory] = None

    model_config = ConfigDict(from_attributes=True)
