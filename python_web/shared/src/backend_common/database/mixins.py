"""Reusable SQLAlchemy ORM mixins for common column patterns.

Provides timestamp tracking and soft-delete functionality that can be
composed into any model via multiple inheritance.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Mixin that adds ``created_at`` and ``updated_at`` timestamp columns.

    Both columns default to the current UTC time and ``updated_at`` is
    automatically refreshed on each update.

    Attributes:
        created_at: Row creation timestamp (UTC).
        updated_at: Last modification timestamp (UTC).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SoftDeleteMixin:
    """Mixin that adds soft-delete support via ``is_deleted`` and ``deleted_at`` columns.

    Attributes:
        is_deleted: Whether the row has been soft-deleted.
        deleted_at: Timestamp of the soft deletion, or None if active.
    """
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )