"""Mixin for soft-delete behavior in SQLAdmin views with cascading support."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import inspect as sa_inspect
from sqlalchemy import update
from starlette.requests import Request


logger = logging.getLogger(__name__)


def _cast_pk(model: Any, pk: Any) -> Any:
    """Cast a primary key value to the column's Python type."""
    pk_cols = sa_inspect(model).mapper.primary_key
    if len(pk_cols) == 1:
        col_type = pk_cols[0].type.python_type
        return col_type(pk)
    return pk


class SoftDeleteMixin:
    """Override delete_model to set is_deleted=True instead of hard-deleting.

    Subclasses may define ``_cascade_soft_delete_models`` as a list of
    ``(RelatedModel, fk_column)`` tuples to cascade soft-delete to related
    entities when the parent is deleted.
    """

    _cascade_soft_delete_models: list[tuple] = []

    async def delete_model(self, request: Request, pk: Any) -> None:
        pk = _cast_pk(self.model, pk)

        async with self.session_maker() as session:
            obj = await session.get(self.model, pk)
            if obj is None:
                return

            await self.on_model_delete(obj, request)

            obj.is_deleted = True
            if hasattr(obj, "is_active"):
                obj.is_active = False

            for cascade_entry in self._cascade_soft_delete_models:
                related_model, fk_column = cascade_entry[0], cascade_entry[1]
                values = (
                    cascade_entry[2]
                    if len(cascade_entry) > 2
                    else {"is_deleted": True, "is_active": False}
                )

                conditions = [fk_column == pk]
                if hasattr(related_model, "is_deleted"):
                    conditions.append(related_model.is_deleted.is_(False))

                stmt = update(related_model).where(*conditions).values(**values)
                result = await session.execute(stmt)
                if result.rowcount:
                    logger.info(
                        "Cascade soft-deleted %d %s for %s pk=%s",
                        result.rowcount,
                        related_model.__tablename__,
                        self.model.__tablename__,
                        pk,
                    )

            await session.commit()
            await self.after_model_delete(obj, request)
