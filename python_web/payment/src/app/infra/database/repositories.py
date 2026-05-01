"""SQLAlchemy implementations of order and payment repository interfaces."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.order.entities import Order, OrderStatus
from src.app.core.order.repository import IOrderRepository
from src.app.core.payment.entities import Payment, PaymentStatus
from src.app.core.payment.repository import IPaymentRepository
from src.app.infra.database.models import OrderDB, OrderItemDB, PaymentDB


class SqlAlchemyOrderRepository(IOrderRepository):
    """SQLAlchemy-based implementation of the order repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an async database session.

        Args:
            session: The SQLAlchemy async session.
        """
        self.session = session

    async def create(self, order: Order) -> Order:
        """Persist a new order with its items.

        Args:
            order: The order domain entity to store.

        Returns:
            The persisted order with generated timestamps.
        """
        db_order = OrderDB.from_domain(order)
        self.session.add(db_order)
        await self.session.flush()

        # Add items
        for item in order.items:
            db_item = OrderItemDB.from_domain(item)
            self.session.add(db_item)
        await self.session.flush()

        await self.session.refresh(db_order)
        return db_order.to_domain()

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Retrieve an order by its primary key.

        Args:
            order_id: The UUID of the order.

        Returns:
            The Order if found, otherwise None.
        """
        result = await self.session.execute(
            select(OrderDB).where(OrderDB.id == order_id)
        )
        db_order = result.scalar_one_or_none()
        return db_order.to_domain() if db_order else None

    async def get_by_user_id(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Order], int]:
        """Retrieve paginated orders for a user, ordered by creation date descending.

        Args:
            user_id: The owner's UUID.
            offset: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            Tuple of (list of orders, total count).
        """
        # Count
        count_result = await self.session.execute(
            select(func.count()).select_from(OrderDB).where(OrderDB.user_id == user_id)
        )
        total = count_result.scalar_one()

        # Fetch
        result = await self.session.execute(
            select(OrderDB)
            .where(OrderDB.user_id == user_id)
            .order_by(OrderDB.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        orders = [row.to_domain() for row in result.scalars().all()]
        return orders, total

    async def update_status(self, order_id: UUID, status: OrderStatus) -> Order | None:
        """Update an order's status in the database.

        Args:
            order_id: The UUID of the order to update.
            status: The new order status.

        Returns:
            The updated Order if found, otherwise None.
        """
        result = await self.session.execute(
            select(OrderDB).where(OrderDB.id == order_id)
        )
        db_order = result.scalar_one_or_none()
        if not db_order:
            return None
        db_order.status = status.value
        await self.session.flush()
        await self.session.refresh(db_order)
        return db_order.to_domain()


class SqlAlchemyPaymentRepository(IPaymentRepository):
    """SQLAlchemy-based implementation of the payment repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an async database session.

        Args:
            session: The SQLAlchemy async session.
        """
        self.session = session

    async def create(self, payment: Payment) -> Payment:
        """Persist a new payment record.

        Args:
            payment: The payment domain entity to store.

        Returns:
            The persisted payment with generated fields.
        """
        db_payment = PaymentDB.from_domain(payment)
        self.session.add(db_payment)
        await self.session.flush()
        await self.session.refresh(db_payment)
        return db_payment.to_domain()

    async def get_by_order_id(self, order_id: UUID) -> Payment | None:
        """Retrieve a payment by its associated order ID.

        Args:
            order_id: The UUID of the order.

        Returns:
            The Payment if found, otherwise None.
        """
        result = await self.session.execute(
            select(PaymentDB).where(PaymentDB.order_id == order_id)
        )
        db_payment = result.scalar_one_or_none()
        return db_payment.to_domain() if db_payment else None

    async def get_by_provider_id(self, provider_payment_id: str) -> Payment | None:
        """Retrieve a payment by its external provider payment ID.

        Args:
            provider_payment_id: The payment ID from the payment provider.

        Returns:
            The Payment if found, otherwise None.
        """
        stmt = select(PaymentDB).where(
            PaymentDB.provider_payment_id == provider_payment_id
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if not row:
            return None
        return Payment.model_validate(row)

    async def update_status(
        self,
        payment_id: UUID,
        status: PaymentStatus,
        provider_payment_id: str | None = None,
    ) -> Payment | None:
        """Update a payment's status and optionally set the provider ID.

        Args:
            payment_id: The UUID of the payment to update.
            status: The new payment status.
            provider_payment_id: Optional provider ID to associate.

        Returns:
            The updated Payment if found, otherwise None.
        """
        result = await self.session.execute(
            select(PaymentDB).where(PaymentDB.id == payment_id)
        )
        db_payment = result.scalar_one_or_none()
        if not db_payment:
            return None
        db_payment.status = status.value
        if provider_payment_id is not None:
            db_payment.provider_payment_id = provider_payment_id
        await self.session.flush()
        await self.session.refresh(db_payment)
        return db_payment.to_domain()
