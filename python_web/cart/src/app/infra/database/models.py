"""SQLAlchemy ORM models for cart persistence.

Maps the Cart and CartItem domain entities to database tables,
providing bidirectional conversion between domain and ORM representations.
"""

from uuid import uuid4, UUID

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend_common.database.base import Base
from backend_common.database.mixins import TimestampMixin
from src.app.core.cart.entities import Cart, CartItem, CartStatus


class CartDB(Base, TimestampMixin):
    """SQLAlchemy model representing the carts table."""

    __tablename__ = "carts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=CartStatus.ACTIVE.value)

    items: Mapped[list["CartItemDB"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan", lazy="selectin"
    )

    def to_domain(self) -> Cart:
        """Convert this ORM model to a Cart domain entity.

        Returns:
            A Cart domain entity populated from this record.
        """
        return Cart(
            id=self.id,
            user_id=self.user_id,
            items=[item.to_domain() for item in self.items],
            status=CartStatus(self.status),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, cart: Cart) -> "CartDB":
        """Create a CartDB instance from a Cart domain entity.

        Args:
            cart: The domain entity to convert.

        Returns:
            A new CartDB ORM instance.
        """
        return cls(
            id=cart.id,
            user_id=cart.user_id,
            status=cart.status.value,
        )


class CartItemDB(Base, TimestampMixin):
    """SQLAlchemy model representing the cart_items table."""

    __tablename__ = "cart_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cart_id: Mapped[UUID] = mapped_column(
        ForeignKey("carts.id"), index=True, nullable=False
    )
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    product_title: Mapped[str] = mapped_column(String(500), nullable=False)
    product_image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    cart: Mapped["CartDB"] = relationship(back_populates="items")

    def to_domain(self) -> CartItem:
        """Convert this ORM model to a CartItem domain entity.

        Returns:
            A CartItem domain entity populated from this record.
        """
        return CartItem(
            id=self.id,
            cart_id=self.cart_id,
            product_id=self.product_id,
            quantity=self.quantity,
            unit_price=self.unit_price,
            product_title=self.product_title,
            product_image_url=self.product_image_url,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, item: CartItem) -> "CartItemDB":
        """Create a CartItemDB instance from a CartItem domain entity.

        Args:
            item: The domain entity to convert.

        Returns:
            A new CartItemDB ORM instance.
        """
        return cls(
            id=item.id,
            cart_id=item.cart_id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            product_title=item.product_title,
            product_image_url=item.product_image_url,
        )
