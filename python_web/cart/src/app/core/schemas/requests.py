"""Request schemas for cart operations.

Defines Pydantic models used to validate and parse incoming request
payloads for adding items to the cart and updating item quantities.
"""

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration for all cart request models."""

    model_config = ConfigDict(str_strip_whitespace=True)


class AddToCartRequest(BaseSchema):
    """Request payload for adding a product to the cart.

    Attributes:
        product_id: The identifier of the product to add.
        quantity: The number of units to add (must be greater than 0).
    """

    product_id: int
    quantity: int = Field(gt=0)


class UpdateCartItemRequest(BaseSchema):
    """Request payload for updating a cart item's quantity.

    Attributes:
        quantity: The new quantity for the cart item (must be greater than 0).
    """

    quantity: int = Field(gt=0)
