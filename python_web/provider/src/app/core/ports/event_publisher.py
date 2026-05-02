"""Port interface for domain event publishing."""

from typing import Protocol


class IEventPublisher(Protocol):
    """Port for publishing domain events to a message broker."""

    async def publish_product_created(self, product_data: dict) -> None:
        """Publish a product creation event.

        Args:
            product_data: Product payload to include in the event.
        """
        pass

    async def publish_product_updated(self, product_data: dict) -> None:
        """Publish a product update event.

        Args:
            product_data: Updated product payload.
        """
        pass

    async def publish_product_deleted(self, product_id: int, supplier_id: int) -> None:
        """Publish a product deletion event.

        Args:
            product_id: ID of the product to delete.
            supplier_id: ID of the owning seller.
        """
        pass

    async def publish_seller_created(self, seller_data: dict) -> None:
        """Publish a seller profile creation event.

        Args:
            seller_data: Seller payload to include in the event.
        """
        pass

    async def publish_seller_updated(self, seller_data: dict) -> None:
        """Publish a seller profile update event.

        Args:
            seller_data: Updated seller payload.
        """
        pass

    async def publish_order_status_updated(self, payload: dict) -> None:
        """Publish a vendor order status update event.

        Args:
            payload: Order status change payload.
        """
        pass
