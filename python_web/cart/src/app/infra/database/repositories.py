"""SQLAlchemy implementation of the cart repository.

Provides concrete database operations for cart and cart item persistence
using async SQLAlchemy sessions.
"""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.core.cart.entities import Cart, CartItem, CartStatus
from src.app.core.cart.repository import ICartRepository
from src.app.infra.database.models import CartDB, CartItemDB


class SqlAlchemyCartRepository(ICartRepository):
    """Concrete cart repository backed by SQLAlchemy and PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Async SQLAlchemy session for database operations.
        """
        self.session = session

    async def get_active_cart_by_user(self, user_id: UUID) -> Cart | None:
        """Find the active cart for a given user.

        Args:
            user_id: The user's unique identifier.

        Returns:
            The active cart domain entity, or None if no active cart exists.
        """
        result = await self.session.execute(
            select(CartDB)
            .options(selectinload(CartDB.items))
            .where(
                CartDB.user_id == user_id,
                CartDB.status == CartStatus.ACTIVE.value,
            )
        )
        db_cart = result.scalar_one_or_none()
        return db_cart.to_domain() if db_cart else None

    async def create(self, cart: Cart) -> Cart:
        """Persist a new cart to the database.

        Args:
            cart: The cart domain entity to save.

        Returns:
            The saved cart entity with generated fields populated.
        """
        db_cart = CartDB.from_domain(cart)
        self.session.add(db_cart)
        await self.session.flush()
        await self.session.refresh(db_cart)
        return db_cart.to_domain()

    async def update(self, cart: Cart) -> Cart:
        """Update an existing cart's status in the database.

        Args:
            cart: The cart domain entity with updated fields.

        Returns:
            The updated cart entity.
        """
        result = await self.session.execute(select(CartDB).where(CartDB.id == cart.id))
        db_cart = result.scalar_one()
        db_cart.status = cart.status.value
        await self.session.flush()
        await self.session.refresh(db_cart)
        return db_cart.to_domain()

    async def add_item(self, item: CartItem) -> CartItem:
        """Add a new item to a cart in the database.

        Args:
            item: The cart item domain entity to persist.

        Returns:
            The saved cart item entity.
        """
        db_item = CartItemDB.from_domain(item)
        self.session.add(db_item)
        await self.session.flush()
        await self.session.refresh(db_item)
        return db_item.to_domain()

    async def update_item(self, item: CartItem) -> CartItem:
        """Update an existing cart item's quantity and price.

        Args:
            item: The cart item domain entity with updated fields.

        Returns:
            The updated cart item entity.
        """
        result = await self.session.execute(
            select(CartItemDB).where(
                CartItemDB.id == item.id,
                CartItemDB.cart_id == item.cart_id,
            )
        )
        db_item = result.scalar_one()
        db_item.quantity = item.quantity
        db_item.unit_price = item.unit_price
        await self.session.flush()
        await self.session.refresh(db_item)
        return db_item.to_domain()

    async def remove_item(self, item_id: UUID, cart_id: UUID) -> None:
        """Delete a cart item from the database.

        Args:
            item_id: The item's unique identifier.
            cart_id: The cart's unique identifier.
        """
        await self.session.execute(
            delete(CartItemDB).where(
                CartItemDB.id == item_id,
                CartItemDB.cart_id == cart_id,
            )
        )
        await self.session.flush()

    async def get_item_by_id(self, item_id: UUID, cart_id: UUID) -> CartItem | None:
        """Find a cart item by its ID within a specific cart.

        Args:
            item_id: The item's unique identifier.
            cart_id: The cart's unique identifier.

        Returns:
            The cart item domain entity, or None if not found.
        """
        result = await self.session.execute(
            select(CartItemDB).where(
                CartItemDB.id == item_id,
                CartItemDB.cart_id == cart_id,
            )
        )
        db_item = result.scalar_one_or_none()
        return db_item.to_domain() if db_item else None

    async def get_item_by_product(
        self, cart_id: UUID, product_id: int
    ) -> CartItem | None:
        """Find a cart item by product ID within a specific cart.

        Args:
            cart_id: The cart's unique identifier.
            product_id: The product identifier to search for.

        Returns:
            The cart item domain entity, or None if not found.
        """
        result = await self.session.execute(
            select(CartItemDB).where(
                CartItemDB.cart_id == cart_id,
                CartItemDB.product_id == product_id,
            )
        )
        db_item = result.scalar_one_or_none()
        return db_item.to_domain() if db_item else None

    async def clear_items(self, cart_id: UUID) -> None:
        """Delete all items belonging to a cart.

        Args:
            cart_id: The cart's unique identifier.
        """
        await self.session.execute(
            delete(CartItemDB).where(CartItemDB.cart_id == cart_id)
        )
        await self.session.flush()
