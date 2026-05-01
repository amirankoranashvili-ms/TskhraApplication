"""SQLAlchemy declarative base for all database models.

All ORM models across backend services should inherit from the ``Base``
class defined here to share a single metadata registry.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base class for all SQLAlchemy ORM models."""

    pass