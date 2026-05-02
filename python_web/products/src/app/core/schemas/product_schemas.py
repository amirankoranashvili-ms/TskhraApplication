"""Product API schemas.

Pydantic models for product-related API requests and responses,
including creation, update, search, and detail payloads.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from src.app.core.products.entities import Product, Brand


class GetProductResponse(BaseModel):
    """Response schema wrapping a single full product."""

    product: Product


class ProductSlim(BaseModel):
    """Lightweight product representation for list and search results."""

    id: int
    brand: Brand
    price: float
    title: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    stock_quantity: int = 0
    sku: str = ""
    images: List[str] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator("images", mode="before")
    @classmethod
    def extract_image_urls(cls, v: Any) -> List[str]:
        """Extract image URL strings from ORM image objects if needed.

        Args:
            v: A list of strings or ORM image objects with image_url attribute.

        Returns:
            A list of image URL strings.
        """
        if v and not isinstance(v[0], str):
            return [img.image_url for img in v]
        return v


class ProductSearchResponse(BaseModel):
    """Paginated response for product list and search endpoints."""

    items: List[ProductSlim]
    total: int
    page: int
    limit: int
    total_pages: int


class Spec(BaseModel):
    """A specification entry linking a field to a chosen option."""

    field_id: int
    option_id: int


class ProductCreateRequest(BaseModel):
    """Request schema for creating a new product."""

    category_id: int
    supplier_id: int
    brand_id: int
    cover_image_url: Optional[str] = None
    title: str
    description: Optional[str] = None
    price: float
    sku: str
    stock_quantity: int = 0
    images: List[str] = []
    specifications: List[Spec] = []

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def map_quantity_to_stock(cls, data: Any) -> Any:
        if (
            isinstance(data, dict)
            and "quantity" in data
            and "stock_quantity" not in data
        ):
            data["stock_quantity"] = data["quantity"]
        return data


class ProductUpdateRequest(BaseModel):
    """Request schema for updating an existing product. All fields optional."""

    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    cover_image_url: Optional[str] = None
    images: Optional[List[str]] = None
    deleted_images: List[str] = []
    specifications: Optional[List[Spec]] = None

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def map_quantity_to_stock(cls, data: Any) -> Any:
        if (
            isinstance(data, dict)
            and "quantity" in data
            and "stock_quantity" not in data
        ):
            data["stock_quantity"] = data["quantity"]
        return data
