"""Sorting utilities for product queries.

Implements the Chain of Responsibility pattern for applying different
sort strategies to SQLAlchemy product queries.
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.app.core.products.entities import SortByOption
from src.app.infra.database.models import ProductDb as ProductORM


class SortHandler(ABC):
    """Abstract base handler in the sort chain of responsibility."""

    def __init__(self):
        self._next_handler: Optional["SortHandler"] = None

    def set_next(self, handler: "SortHandler") -> "SortHandler":
        """Set the next handler in the chain.

        Args:
            handler: The next sort handler to delegate to.

        Returns:
            The handler that was set, for fluent chaining.
        """
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, stmt, sort_by: SortByOption):
        """Apply sorting if this handler matches, otherwise delegate.

        Args:
            stmt: The SQLAlchemy select statement.
            sort_by: The requested sort option.

        Returns:
            The statement with ordering applied.
        """
        if self._next_handler:
            return self._next_handler.handle(stmt, sort_by)
        return stmt.order_by(ProductORM.created_at.desc())


class PriceAscSortHandler(SortHandler):
    """Sort handler for ascending price ordering."""

    def handle(self, stmt, sort_by: SortByOption):
        if sort_by == SortByOption.PRICE_ASC:
            return stmt.order_by(ProductORM.price.asc())
        return super().handle(stmt, sort_by)


class PriceDescSortHandler(SortHandler):
    """Sort handler for descending price ordering."""

    def handle(self, stmt, sort_by: SortByOption):
        if sort_by == SortByOption.PRICE_DESC:
            return stmt.order_by(ProductORM.price.desc())
        return super().handle(stmt, sort_by)


class NewestSortHandler(SortHandler):
    """Sort handler for newest-first ordering by creation date."""

    def handle(self, stmt, sort_by: SortByOption):
        if sort_by == SortByOption.NEWEST:
            return stmt.order_by(ProductORM.created_at.desc())
        return super().handle(stmt, sort_by)


class PopularSortHandler(SortHandler):
    """Sort handler for popularity ordering (falls back to newest)."""

    def handle(self, stmt, sort_by: SortByOption):
        if sort_by == SortByOption.POPULAR:
            # Fallback to newest until we have a popularity score column
            return stmt.order_by(ProductORM.created_at.desc())
        return super().handle(stmt, sort_by)
