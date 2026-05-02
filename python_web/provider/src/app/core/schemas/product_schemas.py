"""Request schemas for product management operations.

Defines Pydantic models for product creation, update, and
image deletion requests.
"""

from pydantic import BaseModel, ConfigDict, Field


class Specification(BaseModel):
    """Represents a product specification key-value pair.

    Attributes:
        field_id: ID of the specification field.
        option_id: ID of the selected option for the field.
    """

    field_id: int
    option_id: int


class ProductCreateRequest(BaseModel):
    """Request schema for creating a new product.

    Attributes:
        category_id: ID of the product category.
        brand_id: ID of the product brand.
        title: Product display title.
        description: Optional product description.
        price: Product price (must be positive).
        quantity: Available stock quantity.
        sku: Stock keeping unit identifier.
        specifications: List of product specifications.
    """

    category_id: int = Field(..., gt=0)
    brand_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    sku: str = Field(..., min_length=2)
    specifications: list[Specification] = []

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    """Request schema for updating an existing product.

    All fields are optional to support partial updates.

    Attributes:
        category_id: Updated category ID.
        brand_id: Updated brand ID.
        title: Updated product title.
        description: Updated product description.
        price: Updated product price.
        specifications: Updated list of product specifications.
    """

    category_id: int | None = None
    brand_id: int | None = None
    title: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    specifications: list[Specification] = []

    model_config = ConfigDict(from_attributes=True)


class DeleteImagesRequest(BaseModel):
    """Request schema for deleting images from a product draft.

    Attributes:
        image_urls: List of image URLs to remove from the draft.
    """

    image_urls: list[str]
