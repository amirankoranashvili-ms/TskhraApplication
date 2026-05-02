"""Service layer for processing verification requests (approve/reject)."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Protocol

from backend_common.exceptions import ConflictException, EntityNotFoundException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.app.core.constants import (
    VendorStatus,
    VerificationRequestType,
    VerificationStatus,
)
from src.app.infra.database.models.products import (
    PlatformSellerDb,
    ProductDb,
    VerificationRequestDb,
)
from src.app.infra.database.models.vendor import VendorSellerDb

logger = logging.getLogger(__name__)


class VerificationHandler(Protocol):
    """Protocol defining the interface for verification type handlers."""

    async def approve(
        self,
        vr: Any,
        products_session: AsyncSession,
        vendor_session: AsyncSession,
        publisher: Any,
    ) -> None: ...
    async def reject(
        self,
        vr: Any,
        reason: str,
        products_session: AsyncSession,
        vendor_session: AsyncSession,
        publisher: Any,
    ) -> None: ...


class SellerVerificationHandler:
    """Handles approval and rejection of seller verification requests."""

    async def approve(self, vr, products_session, vendor_session, publisher):
        """Approve a seller verification request.

        Args:
            vr: The verification request database record.
            products_session: Async session for the products database.
            vendor_session: Async session for the vendor database.
            publisher: Event publisher for sending broker messages.
        """
        await asyncio.gather(
            products_session.execute(
                update(PlatformSellerDb)
                .where(PlatformSellerDb.supplier_id == vr.supplier_id)
                .values(is_active=True)
            ),
            vendor_session.execute(
                update(VendorSellerDb)
                .where(VendorSellerDb.supplier_id == vr.supplier_id)
                .values(status=VendorStatus.ACTIVE.value)
            ),
        )
        logger.info("Seller %s approved", vr.supplier_id)

    async def reject(self, vr, reason, products_session, vendor_session, publisher):
        """Reject a seller verification request.

        Args:
            vr: The verification request database record.
            reason: Human-readable rejection reason.
            products_session: Async session for the products database.
            vendor_session: Async session for the vendor database.
            publisher: Event publisher for sending broker messages.
        """
        await asyncio.gather(
            products_session.execute(
                update(PlatformSellerDb)
                .where(PlatformSellerDb.supplier_id == vr.supplier_id)
                .values(is_active=False)
            ),
            vendor_session.execute(
                update(VendorSellerDb)
                .where(VendorSellerDb.supplier_id == vr.supplier_id)
                .values(status=VendorStatus.REJECTED.value)
            ),
        )
        logger.info("Seller %s rejected: %s", vr.supplier_id, reason)


class ProductVerificationHandler:
    """Handles approval and rejection of product verification requests."""

    async def approve(self, vr, products_session, vendor_session, publisher):
        """Approve a product verification request.

        Args:
            vr: The verification request database record.
            products_session: Async session for the products database.
            vendor_session: Async session for the vendor database (unused for products).
            publisher: Event publisher for sending broker messages.
        """
        await products_session.execute(
            update(ProductDb)
            .where(ProductDb.id == vr.product_id)
            .values(is_active=True)
        )
        if publisher:
            await publisher.publish(
                "product.verified",
                {
                    "product_id": vr.product_id,
                    "supplier_id": vr.supplier_id,
                    "status": "APPROVED",
                },
            )
        logger.info("Product %s approved", vr.product_id)

    async def reject(self, vr, reason, products_session, vendor_session, publisher):
        """Reject a product verification request.

        Args:
            vr: The verification request database record.
            reason: Human-readable rejection reason.
            products_session: Async session for the products database.
            vendor_session: Async session for the vendor database (unused for products).
            publisher: Event publisher for sending broker messages.
        """
        await products_session.execute(
            update(ProductDb)
            .where(ProductDb.id == vr.product_id)
            .values(is_deleted=True, is_active=False)
        )
        if publisher:
            await publisher.publish(
                "product.upload.rejected",
                {
                    "product_id": vr.product_id,
                    "supplier_id": vr.supplier_id,
                    "error_message": reason,
                },
            )
        logger.info("Product %s rejected: %s", vr.product_id, reason)


VERIFICATION_HANDLERS: dict[str, VerificationHandler] = {
    VerificationRequestType.SELLER.value: SellerVerificationHandler(),
    VerificationRequestType.PRODUCT.value: ProductVerificationHandler(),
}


class VerificationService:
    """Core service for listing, approving, and rejecting verification requests."""

    def __init__(
        self,
        products_session: AsyncSession,
        vendor_session: AsyncSession,
        publisher=None,
    ) -> None:
        """Initialise the verification service.

        Args:
            products_session: Async session bound to the products database.
            vendor_session: Async session bound to the vendor database.
            publisher: Optional event publisher for broker notifications.
        """
        self.products_session = products_session
        self.vendor_session = vendor_session
        self.publisher = publisher

    async def list_pending(self) -> list[dict[str, Any]]:
        """Return all pending verification requests ordered by newest first.

        Returns:
            A list of dictionaries representing pending verification requests.
        """
        result = await self.products_session.execute(
            select(
                VerificationRequestDb.id,
                VerificationRequestDb.request_type,
                VerificationRequestDb.status,
                VerificationRequestDb.supplier_id,
                VerificationRequestDb.product_id,
                VerificationRequestDb.rejection_reason,
                VerificationRequestDb.created_at,
            )
            .where(VerificationRequestDb.status == VerificationStatus.PENDING.value)
            .order_by(VerificationRequestDb.id.desc())
        )
        return [
            {
                "id": r.id,
                "request_type": r.request_type,
                "status": r.status,
                "supplier_id": r.supplier_id,
                "product_id": r.product_id,
                "rejection_reason": r.rejection_reason,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in result.all()
        ]

    async def get_with_product(self, request_id: int):
        """Fetch a verification request together with its associated product.

        Args:
            request_id: Primary key of the verification request.

        Returns:
            A tuple of (verification_request, product) where product may be None.
        """
        result = await self.products_session.execute(
            select(VerificationRequestDb)
            .options(joinedload(VerificationRequestDb.product))
            .where(VerificationRequestDb.id == request_id)
        )
        vr = result.unique().scalar_one_or_none()
        return vr, vr.product if vr else None

    async def _get_pending_request(self, request_id: int) -> VerificationRequestDb:
        """Retrieve a verification request that must still be pending.

        Args:
            request_id: Primary key of the verification request.

        Returns:
            The pending VerificationRequestDb instance.

        Raises:
            EntityNotFoundException: If the request does not exist.
            ConflictException: If the request has already been resolved.
        """
        vr = await self.products_session.get(VerificationRequestDb, request_id)
        if not vr:
            raise EntityNotFoundException("Verification request not found")
        if vr.status != VerificationStatus.PENDING.value:
            raise ConflictException("Verification request already resolved")
        return vr

    def _get_handler(self, vr: VerificationRequestDb) -> VerificationHandler:
        """Look up the handler for a verification request's type.

        Args:
            vr: The verification request whose type determines the handler.

        Returns:
            A VerificationHandler for the request type.

        Raises:
            ConflictException: If the request type is unknown.
        """
        handler = VERIFICATION_HANDLERS.get(vr.request_type)
        if not handler:
            raise ConflictException(f"Unknown verification type: {vr.request_type}")
        return handler

    async def approve(self, request_id: int, admin_username: str) -> dict[str, Any]:
        """Approve a pending verification request.

        Args:
            request_id: Primary key of the verification request.
            admin_username: Username of the admin performing the action.

        Returns:
            A dict containing the request id and its new status.

        Raises:
            EntityNotFoundException: If the request does not exist.
            ConflictException: If the request has already been resolved.
        """
        vr = await self._get_pending_request(request_id)
        handler = self._get_handler(vr)

        await handler.approve(
            vr, self.products_session, self.vendor_session, self.publisher
        )

        vr.status = VerificationStatus.APPROVED.value
        vr.resolved_by_admin_id = admin_username
        vr.resolved_at = datetime.utcnow()

        await self.products_session.commit()
        try:
            await self.vendor_session.commit()
        except Exception:
            logger.error(
                "Vendor DB commit failed after products commit for request %s — data may be inconsistent",
                request_id,
            )
            raise

        return {"id": request_id, "status": "approved"}

    async def reject(
        self, request_id: int, admin_username: str, rejection_reason: str
    ) -> dict[str, Any]:
        """Reject a pending verification request.

        Args:
            request_id: Primary key of the verification request.
            admin_username: Username of the admin performing the action.
            rejection_reason: Human-readable reason for the rejection.

        Returns:
            A dict containing the request id, status, and rejection reason.

        Raises:
            EntityNotFoundException: If the request does not exist.
            ConflictException: If the request has already been resolved.
        """
        vr = await self._get_pending_request(request_id)
        handler = self._get_handler(vr)

        await handler.reject(
            vr,
            rejection_reason,
            self.products_session,
            self.vendor_session,
            self.publisher,
        )

        vr.status = VerificationStatus.REJECTED.value
        vr.resolved_by_admin_id = admin_username
        vr.rejection_reason = rejection_reason
        vr.resolved_at = datetime.utcnow()

        await self.products_session.commit()
        try:
            await self.vendor_session.commit()
        except Exception:
            logger.error(
                "Vendor DB commit failed after products commit for request %s — data may be inconsistent",
                request_id,
            )
            raise

        return {"id": request_id, "status": "rejected", "reason": rejection_reason}
