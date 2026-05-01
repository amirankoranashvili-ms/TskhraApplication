"""Re-exports the shared SQLAlchemy declarative Base for admin models."""

from backend_common.database.base import Base

__all__ = ["Base"]
