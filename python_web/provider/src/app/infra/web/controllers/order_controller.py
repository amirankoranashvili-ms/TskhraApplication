"""FastAPI controller for vendor order management endpoints.

Defines API routes for listing, retrieving, and updating the status
of vendor orders.
"""

from typing import Annotated
from uuid import UUID

from backend_common.error_handlers import merge_responses
from fastapi import APIRouter, Depends, Path, Query, status

from src.app.core.orders.entities import VendorOrderStatus
from src.app.core.schemas.order_schemas import (
    UpdateOrderStatusRequest,
    VendorOrderPaginatedResponse,
    VendorOrderResponse,
)
from src.app.infra.auth.auth import get_current_user_id
from src.app.infra.web.dependables import SellerServiceDep, VendorOrderServiceDep
from src.app.infra.web.handler import (
    InvalidStatusTransitionResponse,
    NotAuthenticatedResponse,
    SellerNotFoundResponse,
    VendorOrderNotFoundResponse,
)

vendor_orders_api = APIRouter(prefix="/{supplier_id}/orders", tags=["Vendor Orders"])


@vendor_orders_api.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
    ),
)
async def get_vendor_orders(
    seller_service: SellerServiceDep,
    order_service: VendorOrderServiceDep,
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    order_status: VendorOrderStatus | None = Query(
        None, alias="status", description="Filter by status"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> VendorOrderPaginatedResponse:
    """Get paginated vendor orders with optional status filter.

    Args:
        seller_service: Seller service for authorization.
        order_service: Vendor order service dependency.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.
        order_status: Optional status filter.
        page: Page number.
        limit: Items per page.

    Returns:
        Paginated response with vendor orders.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)
    orders, total = await order_service.get_orders(
        supplier_id, order_status, page, limit
    )
    return VendorOrderPaginatedResponse(
        orders=[o.model_dump() for o in orders],
        total=total,
        page=page,
        limit=limit,
    )


@vendor_orders_api.get(
    "/{vendor_order_id}",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
        VendorOrderNotFoundResponse,
    ),
)
async def get_vendor_order(
    seller_service: SellerServiceDep,
    order_service: VendorOrderServiceDep,
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    vendor_order_id: Annotated[UUID, Path(..., description="The vendor order ID")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> VendorOrderResponse:
    """Get a specific vendor order by its ID.

    Args:
        seller_service: Seller service for authorization.
        order_service: Vendor order service dependency.
        supplier_id: ID of the vendor/supplier.
        vendor_order_id: UUID of the vendor order.
        user_id: Authenticated user's UUID.

    Returns:
        The vendor order response.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)
    order = await order_service.get_order(vendor_order_id)
    return VendorOrderResponse.model_validate(order.model_dump())


@vendor_orders_api.patch(
    "/{vendor_order_id}/status",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
        VendorOrderNotFoundResponse,
        InvalidStatusTransitionResponse,
    ),
)
async def update_vendor_order_status(
    seller_service: SellerServiceDep,
    order_service: VendorOrderServiceDep,
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    vendor_order_id: Annotated[UUID, Path(..., description="The vendor order ID")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    body: UpdateOrderStatusRequest,
) -> VendorOrderResponse:
    """Update the status of a vendor order.

    Args:
        seller_service: Seller service for authorization.
        order_service: Vendor order service dependency.
        supplier_id: ID of the vendor/supplier.
        vendor_order_id: UUID of the vendor order.
        user_id: Authenticated user's UUID.
        body: Request body with the target status.

    Returns:
        The updated vendor order response.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)
    order = await order_service.update_status(vendor_order_id, body.status)
    return VendorOrderResponse.model_validate(order.model_dump())
