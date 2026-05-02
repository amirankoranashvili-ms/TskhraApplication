"""Domain entities for the product upload bounded context.

Defines the product upload task model and its lifecycle status enumeration.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Status(str, Enum):
    """Lifecycle status of a product upload task."""

    Draft = "Draft"
    Pending = "Pending"
    Completed = "Completed"
    Failed = "Failed"
    Rejected = "Rejected"


class ProductUploadTask(BaseModel):
    """Represents a product upload or update task in the review pipeline.

    Attributes:
        task_id: Unique identifier for the task.
        product_id: Associated product ID (set after catalog creation).
        supplier_id: ID of the seller who owns this task.
        status: Current lifecycle status.
        payload: JSON payload containing product data.
        error_message: Error details if the task failed or was rejected.
        created_at: Timestamp of task creation.
        updated_at: Timestamp of last update.
    """

    task_id: UUID
    product_id: int | None = None
    supplier_id: int
    status: Status
    payload: dict[str, Any]
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
