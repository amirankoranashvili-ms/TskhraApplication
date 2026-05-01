"""Service layer for vendor product operations.

Provides product deletion and listing functionality, combining local
draft tasks with live catalog data.
"""

from typing import Any

from src.app.core.ports.catalog_client import ICatalogClient
from src.app.core.ports.event_publisher import IEventPublisher
from src.app.core.products.exceptions import (
    CatalogServiceUnavailableException,
    VendorProductException,
)
from src.app.core.products.repository import IProductTaskRepository


class VendorProductService:
    """Service for vendor product management operations.

    Handles product deletion via event publishing and aggregates
    live catalog products with local draft tasks for listing.
    """

    def __init__(
        self,
        publisher: IEventPublisher,
        http_client: ICatalogClient,
        task_repo: IProductTaskRepository,
    ):
        """Initialize the vendor product service.

        Args:
            publisher: Event publisher for product domain events.
            http_client: HTTP client for the catalog service.
            task_repo: Repository for product upload tasks.
        """
        self.publisher = publisher
        self.http_client = http_client
        self.task_repo = task_repo

    async def delete_product(self, supplier_id: int, product_id: int) -> dict:
        """Delete a product by publishing a deletion event.

        Args:
            supplier_id: ID of the owning seller.
            product_id: ID of the product to delete.

        Returns:
            Status dict with pending deletion confirmation.

        Raises:
            CatalogServiceUnavailableException: If the catalog is unreachable.
            VendorProductException: If the product is not found or access denied.
        """
        product = await self.http_client.get_product_by_id(product_id)
        if product is None:
            raise CatalogServiceUnavailableException()
        if product.get("product", {}).get("supplier_id") != supplier_id:
            raise VendorProductException(message="Product not found or access denied.")
        await self.publisher.publish_product_deleted(product_id, supplier_id)

        task = await self.task_repo.get_task_by_product_id(product_id)
        if task:
            await self.task_repo.delete_task(task.task_id)

        return {"status": "PENDING", "message": "Product deletion event published."}

    async def get_my_products(
        self, supplier_id: int, page: int, limit: int
    ) -> dict[str, Any]:
        """Get combined live and draft products for a vendor.

        Args:
            supplier_id: ID of the seller.
            page: Page number for live product pagination.
            limit: Number of live products per page.

        Returns:
            Dict containing 'live_products' and 'drafts' lists.

        Raises:
            CatalogServiceUnavailableException: If the catalog is unreachable.
        """
        live_products_response = await self.http_client.get_vendor_products(
            supplier_id=supplier_id, page=page, limit=limit
        )

        if live_products_response is None:
            raise CatalogServiceUnavailableException()

        local_tasks = await self.task_repo.get_tasks_by_supplier(
            supplier_id,
            statuses=["Draft", "Pending", "Failed", "Rejected", "Completed"],
        )

        live_items = live_products_response.get("items", [])
        live_product_ids = {item["id"] for item in live_items}

        drafts = []
        for task in local_tasks:
            if task.status.value == "Completed" and task.product_id in live_product_ids:
                continue

            drafts.append(
                {
                    "id": f"{task.task_id}",
                    "title": task.payload.get("title", "Untitled Draft"),
                    "description": task.payload.get("description"),
                    "price": task.payload.get("price", 0),
                    "cover_image_url": task.payload.get("cover_image_url"),
                    "sku": task.payload.get("sku", ""),
                    "quantity": task.payload.get("quantity", 0),
                    "images": task.payload.get("images", []),
                    "upload_status": "Under Review"
                    if task.status.value == "Completed"
                    else task.status.value,
                    "error_message": task.error_message,
                    "created_at": task.created_at.isoformat(),
                }
            )

        return {
            "live_products": live_products_response,
            "drafts": drafts,
        }
