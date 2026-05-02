"""Interactor for retrieving paginated order history."""

import math
from uuid import UUID

from src.app.core.order.service import OrderService
from src.app.core.schemas.responses import (
    OrderItemResponse,
    OrderPaginatedResponse,
    OrderResponse,
)


class GetOrderHistoryInteractor:
    """Fetches paginated order history and builds the API response."""

    def __init__(self, order_service: OrderService) -> None:
        """Initialize with an order service.

        Args:
            order_service: Service for order retrieval.
        """
        self.order_service = order_service

    async def execute(
        self, user_id: UUID, page: int = 1, limit: int = 20
    ) -> OrderPaginatedResponse:
        """Retrieve paginated order history for a user.

        Args:
            user_id: The user whose orders to retrieve.
            page: Page number (1-based).
            limit: Maximum orders per page.

        Returns:
            Paginated response containing orders and metadata.
        """
        orders, total = await self.order_service.get_order_history(user_id, page, limit)
        total_pages = math.ceil(total / limit) if total > 0 else 0

        return OrderPaginatedResponse(
            items=[
                OrderResponse(
                    id=order.id,
                    user_id=order.user_id,
                    items=[
                        OrderItemResponse(
                            id=item.id,
                            entity_id=item.entity_id,
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                            product_title=item.product_title,
                        )
                        for item in order.items
                    ],
                    status=order.status.value,
                    total_amount=order.total_amount,
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                )
                for order in orders
            ],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )
