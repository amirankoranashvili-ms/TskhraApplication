"""SQLAlchemy ORM models for orders and payments."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from backend_common.database.base import Base
from backend_common.database.mixins import TimestampMixin
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.order.entities import Order, OrderItem, OrderStatus
from src.app.core.payment.entities import Payment, PaymentStatus


class OrderDB(Base, TimestampMixin):
    """Database model for orders."""

    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=OrderStatus.PENDING.value)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    items: Mapped[list["OrderItemDB"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )

    def to_domain(self) -> Order:
        """Convert this database model to a domain Order entity.

        Returns:
            An Order domain entity populated from this record.
        """
        return Order(
            id=self.id,
            user_id=self.user_id,
            items=[item.to_domain() for item in self.items],
            status=OrderStatus(self.status),
            total_amount=self.total_amount,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, order: Order) -> "OrderDB":
        """Create a database model instance from a domain Order entity.

        Args:
            order: The domain Order entity.

        Returns:
            An OrderDB instance ready for persistence.
        """
        db_order = cls(
            id=order.id,
            user_id=order.user_id,
            status=order.status.value,
            total_amount=order.total_amount,
        )
        return db_order


class OrderItemDB(Base):
    """Database model for order line items."""

    __tablename__ = "order_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id"), index=True, nullable=False
    )
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    product_title: Mapped[str] = mapped_column(
        "service_type", String(500), nullable=False
    )

    order: Mapped["OrderDB"] = relationship(back_populates="items")

    def to_domain(self) -> OrderItem:
        """Convert this database model to a domain OrderItem entity.

        Returns:
            An OrderItem domain entity populated from this record.
        """
        return OrderItem(
            id=self.id,
            order_id=self.order_id,
            entity_id=self.entity_id,
            quantity=self.quantity,
            unit_price=self.unit_price,
            product_title=self.product_title,
        )

    @classmethod
    def from_domain(cls, item: OrderItem) -> "OrderItemDB":
        """Create a database model instance from a domain OrderItem entity.

        Args:
            item: The domain OrderItem entity.

        Returns:
            An OrderItemDB instance ready for persistence.
        """
        return cls(
            id=item.id,
            order_id=item.order_id,
            entity_id=item.entity_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            product_title=item.product_title,
        )


class PaymentDB(Base):
    """Database model for payment transactions."""

    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=PaymentStatus.PENDING.value)
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def to_domain(self) -> Payment:
        """Convert this database model to a domain Payment entity.

        Returns:
            A Payment domain entity populated from this record.
        """
        return Payment(
            id=self.id,
            order_id=self.order_id,
            amount=self.amount,
            status=PaymentStatus(self.status),
            provider_payment_id=self.provider_payment_id,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, payment: Payment) -> "PaymentDB":
        """Create a database model instance from a domain Payment entity.

        Args:
            payment: The domain Payment entity.

        Returns:
            A PaymentDB instance ready for persistence.
        """
        return cls(
            id=payment.id,
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status.value,
            provider_payment_id=payment.provider_payment_id,
        )
