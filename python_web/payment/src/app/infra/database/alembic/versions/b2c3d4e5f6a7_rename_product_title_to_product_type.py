"""rename product_title column to service_type in order_items

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-17

"""

from typing import Union

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("order_items", "product_title", new_column_name="service_type")


def downgrade() -> None:
    op.alter_column("order_items", "service_type", new_column_name="product_title")
