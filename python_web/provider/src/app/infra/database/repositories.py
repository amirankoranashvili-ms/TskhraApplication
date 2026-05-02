"""SQLAlchemy repository implementations for the provider service.

Provides concrete implementations of the seller, product task, and vendor
order repository protocols using async SQLAlchemy sessions.
"""

from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.core.sellers.exceptions import SellerAlreadyExistsException
from src.app.core.orders.entities import VendorOrder, VendorOrderStatus
from src.app.core.orders.repository import IVendorOrderRepository
from src.app.core.products.entities import ProductUploadTask, Status
from src.app.core.products.repository import IProductTaskRepository
from src.app.core.sellers.entities import PlatformSeller, SellerStatus
from src.app.core.sellers.repository import ISellerRepository
from src.app.infra.database.models import (
    PlatformSellerDb,
    ProductUploadTaskDb,
    VendorOrderDb,
    VendorOrderItemDb,
)


class SqlAlchemySellerRepository(ISellerRepository):
    """SQLAlchemy implementation of the seller repository."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize with a database session.

        Args:
            db_session: Async SQLAlchemy session.
        """
        self.db_session = db_session

    async def create(self, seller_data: PlatformSeller) -> PlatformSeller:
        """Create a new seller record in the database.

        Args:
            seller_data: Seller entity data.

        Returns:
            The created seller with database-generated fields.
        """
        new_seller = PlatformSellerDb(
            user_id=seller_data.user_id,
            name=seller_data.name,
            identification_number=seller_data.identification_number,
            legal_address=seller_data.legal_address,
            contact_phone=seller_data.contact_phone,
            contact_email=seller_data.contact_email,
            bank_account_number=seller_data.bank_account_number,
        )
        self.db_session.add(new_seller)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise SellerAlreadyExistsException()
        await self.db_session.refresh(new_seller)
        return PlatformSeller.model_validate(new_seller)

    async def get_by_user_id_any_status(self, user_id: UUID) -> PlatformSeller | None:
        """Get seller by user ID regardless of status.

        Args:
            user_id: UUID of the owning user.

        Returns:
            The seller entity, or None if not found.
        """
        stmt = select(PlatformSellerDb).where(PlatformSellerDb.user_id == user_id)
        result = await self.db_session.execute(stmt)
        orm_seller = result.scalar_one_or_none()
        if not orm_seller:
            return None
        return PlatformSeller.model_validate(orm_seller)

    async def get_by_identification_number(
        self, identification_number: str
    ) -> PlatformSeller | None:
        """Get seller by identification number.

        Args:
            identification_number: Business or personal ID number.

        Returns:
            The seller entity, or None if not found.
        """
        stmt = select(PlatformSellerDb).where(
            PlatformSellerDb.identification_number == identification_number
        )
        result = await self.db_session.execute(stmt)
        orm_seller = result.scalar_one_or_none()
        if not orm_seller:
            return None
        return PlatformSeller.model_validate(orm_seller)

    async def get_by_user_id(self, user_id: UUID) -> list[PlatformSeller]:
        """Get all seller profiles for a user.

        Args:
            user_id: UUID of the owning user.

        Returns:
            List of seller entities.
        """
        stmt = select(PlatformSellerDb).where(PlatformSellerDb.user_id == user_id)
        result = await self.db_session.execute(stmt)
        orm_sellers = result.scalars().all()
        return [PlatformSeller.model_validate(seller) for seller in orm_sellers]

    async def update(
        self, supplier_id: int, seller_data: PlatformSeller
    ) -> PlatformSeller:
        """Update a seller record and reset status to pending.

        Args:
            supplier_id: ID of the seller to update.
            seller_data: Updated seller data.

        Returns:
            The updated seller entity.
        """
        stmt = (
            update(PlatformSellerDb)
            .where(PlatformSellerDb.supplier_id == supplier_id)
            .values(
                name=seller_data.name,
                identification_number=seller_data.identification_number,
                legal_address=seller_data.legal_address,
                contact_phone=seller_data.contact_phone,
                contact_email=seller_data.contact_email,
                bank_account_number=seller_data.bank_account_number,
                status=SellerStatus.Pending.value,
            )
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

        refreshed = await self.get_by_user_id_any_status(seller_data.user_id)
        return refreshed  # type: ignore

    async def get_by_supplier_id(self, supplier_id: int) -> PlatformSeller | None:
        """Get an active seller by supplier ID.

        Args:
            supplier_id: The supplier identifier.

        Returns:
            The active seller entity, or None if not found.
        """
        stmt = select(PlatformSellerDb).where(
            PlatformSellerDb.supplier_id == supplier_id,
            PlatformSellerDb.status == SellerStatus.Active.value,
        )
        result = await self.db_session.execute(stmt)
        orm_seller = result.scalar_one_or_none()
        if not orm_seller:
            return None
        return PlatformSeller.model_validate(orm_seller)


class SqlAlchemyProductTaskRepository(IProductTaskRepository):
    """SQLAlchemy implementation of the product task repository."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize with a database session.

        Args:
            db_session: Async SQLAlchemy session.
        """
        self.db_session = db_session

    async def create_task(
        self,
        supplier_id: int,
        payload: dict,
        status: str = Status.Pending.value,
        error_message: str | None = None,
        product_id: int | None = None,
    ) -> ProductUploadTask:
        """Create a new product upload task record.

        Args:
            supplier_id: ID of the owning seller.
            payload: Product data as JSON.
            status: Initial task status.
            error_message: Optional error message.
            product_id: Optional associated product ID.

        Returns:
            The created task entity.
        """
        new_task = ProductUploadTaskDb(
            supplier_id=supplier_id,
            payload=payload,
            status=status,
            error_message=error_message,
            product_id=product_id,
        )
        self.db_session.add(new_task)
        await self.db_session.flush()
        await self.db_session.refresh(new_task)
        return ProductUploadTask.model_validate(new_task)

    async def get_task(self, task_id: UUID) -> ProductUploadTask | None:
        """Get a task by its UUID.

        Args:
            task_id: UUID of the task.

        Returns:
            The task entity, or None if not found.
        """
        stmt = select(ProductUploadTaskDb).where(ProductUploadTaskDb.task_id == task_id)
        result = await self.db_session.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            return None
        return ProductUploadTask.model_validate(task)

    async def update_task_payload(self, task_id: UUID, payload: dict) -> None:
        """Update the JSON payload of a task.

        Args:
            task_id: UUID of the task.
            payload: New payload data.
        """
        stmt = (
            update(ProductUploadTaskDb)
            .where(ProductUploadTaskDb.task_id == task_id)
            .values(payload=payload)
        )
        await self.db_session.execute(stmt)

    async def get_draft_by_product_id(
        self, product_id: int
    ) -> ProductUploadTask | None:
        """Get a Draft-status task for a product.

        Args:
            product_id: The product identifier.

        Returns:
            The draft task, or None if not found.
        """
        stmt = select(ProductUploadTaskDb).where(
            ProductUploadTaskDb.product_id == product_id,
            ProductUploadTaskDb.status == Status.Draft.value,
        )
        result = await self.db_session.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            return None
        return ProductUploadTask.model_validate(task)

    async def get_tasks_by_supplier(
        self, supplier_id: int, statuses: list[str]
    ) -> list[ProductUploadTask]:
        """Get tasks for a supplier filtered by status values.

        Args:
            supplier_id: ID of the seller.
            statuses: List of status strings to include.

        Returns:
            List of matching task entities.
        """
        stmt = select(ProductUploadTaskDb).where(
            ProductUploadTaskDb.supplier_id == supplier_id,
            ProductUploadTaskDb.status.in_(statuses),
        )
        result = await self.db_session.execute(stmt)
        tasks = result.scalars().all()
        return [ProductUploadTask.model_validate(t) for t in tasks]

    async def update_task_status(
        self,
        task_id: UUID,
        status: str,
        error_message: str | None = None,
        product_id: int | None = None,
    ) -> None:
        """Update task status and optionally set error message or product ID.

        Args:
            task_id: UUID of the task.
            status: New status value.
            error_message: Optional error description.
            product_id: Optional product ID to associate.
        """
        update_data = {"status": status, "error_message": error_message}

        if product_id is not None:
            update_data["product_id"] = product_id

        stmt = (
            update(ProductUploadTaskDb)
            .where(ProductUploadTaskDb.task_id == task_id)
            .values(**update_data)
        )
        await self.db_session.execute(stmt)

    async def delete_task(self, task_id: UUID) -> None:
        """Delete a task record.

        Args:
            task_id: UUID of the task to delete.
        """
        stmt = delete(ProductUploadTaskDb).where(ProductUploadTaskDb.task_id == task_id)
        await self.db_session.execute(stmt)

    async def reject_task_by_product_id(
        self, product_id: int, error_message: str
    ) -> None:
        """Reject a task by setting its status to Rejected.

        Args:
            product_id: The product identifier.
            error_message: Rejection reason.
        """
        stmt = (
            update(ProductUploadTaskDb)
            .where(ProductUploadTaskDb.product_id == product_id)
            .values(status="Rejected", error_message=error_message)
        )
        await self.db_session.execute(stmt)

    async def get_task_by_product_id(self, product_id: int) -> ProductUploadTask | None:
        """Get a task associated with a product ID.

        Args:
            product_id: The product identifier.

        Returns:
            The matching task, or None if not found.
        """
        stmt = select(ProductUploadTaskDb).where(
            ProductUploadTaskDb.product_id == product_id
        )
        result = await self.db_session.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            return None
        return ProductUploadTask.model_validate(task)


class SqlAlchemyVendorOrderRepository(IVendorOrderRepository):
    """SQLAlchemy implementation of the vendor order repository."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize with a database session.

        Args:
            db_session: Async SQLAlchemy session.
        """
        self.db_session = db_session

    async def create(self, order: VendorOrder) -> VendorOrder:
        """Persist a new vendor order with its items.

        Args:
            order: The vendor order entity to create.

        Returns:
            The persisted vendor order with refreshed data.
        """
        db_order = VendorOrderDb(
            id=order.id,
            order_id=order.order_id,
            supplier_id=order.supplier_id,
            buyer_user_id=order.buyer_user_id,
            status=order.status.value,
            vendor_subtotal=order.vendor_subtotal,
        )
        for item in order.items:
            db_order.items.append(
                VendorOrderItemDb(
                    id=item.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    product_title=item.product_title,
                )
            )
        self.db_session.add(db_order)
        await self.db_session.flush()
        await self.db_session.refresh(db_order, attribute_names=["items"])
        return VendorOrder.model_validate(db_order)

    async def get_by_id(self, vendor_order_id: UUID) -> VendorOrder | None:
        """Get a vendor order by ID with items eagerly loaded.

        Args:
            vendor_order_id: UUID of the vendor order.

        Returns:
            The vendor order, or None if not found.
        """
        stmt = (
            select(VendorOrderDb)
            .options(selectinload(VendorOrderDb.items))
            .where(VendorOrderDb.id == vendor_order_id)
        )
        result = await self.db_session.execute(stmt)
        db_order = result.scalar_one_or_none()
        if not db_order:
            return None
        return VendorOrder.model_validate(db_order)

    async def get_by_supplier_id(
        self,
        supplier_id: int,
        status: VendorOrderStatus | None,
        offset: int,
        limit: int,
    ) -> tuple[list[VendorOrder], int]:
        """Get paginated vendor orders for a supplier.

        Args:
            supplier_id: ID of the vendor.
            status: Optional status filter.
            offset: Records to skip.
            limit: Maximum records to return.

        Returns:
            Tuple of (orders list, total count).
        """
        base = select(VendorOrderDb).where(VendorOrderDb.supplier_id == supplier_id)
        count_base = select(func.count(VendorOrderDb.id)).where(
            VendorOrderDb.supplier_id == supplier_id
        )

        if status:
            base = base.where(VendorOrderDb.status == status.value)
            count_base = count_base.where(VendorOrderDb.status == status.value)

        count_result = await self.db_session.execute(count_base)
        total = count_result.scalar() or 0

        stmt = (
            base.options(selectinload(VendorOrderDb.items))
            .order_by(VendorOrderDb.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db_session.execute(stmt)
        orders = result.scalars().all()
        return [VendorOrder.model_validate(o) for o in orders], total

    async def update_status(
        self, vendor_order_id: UUID, status: VendorOrderStatus
    ) -> VendorOrder | None:
        """Update vendor order status.

        Args:
            vendor_order_id: UUID of the vendor order.
            status: New status value.

        Returns:
            The updated vendor order, or None if not found.
        """
        stmt = (
            update(VendorOrderDb)
            .where(VendorOrderDb.id == vendor_order_id)
            .values(status=status.value)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()
        return await self.get_by_id(vendor_order_id)

    async def exists(self, order_id: UUID, supplier_id: int) -> bool:
        """Check if a vendor order exists for the given order and supplier.

        Args:
            order_id: UUID of the parent customer order.
            supplier_id: ID of the vendor.

        Returns:
            True if a matching record exists.
        """
        stmt = select(func.count(VendorOrderDb.id)).where(
            VendorOrderDb.order_id == order_id,
            VendorOrderDb.supplier_id == supplier_id,
        )
        result = await self.db_session.execute(stmt)
        return (result.scalar() or 0) > 0
