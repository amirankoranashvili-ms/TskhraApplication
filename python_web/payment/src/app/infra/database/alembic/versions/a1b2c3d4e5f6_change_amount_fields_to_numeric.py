"""change amount fields to numeric

Revision ID: a1b2c3d4e5f6
Revises: c7e2f1a4b8d9
Create Date: 2026-04-17

"""

from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "c7e2f1a4b8d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "orders",
        "total_amount",
        type_=sa.Numeric(10, 2),
        existing_type=sa.Float(),
        postgresql_using="total_amount::numeric(10,2)",
    )
    op.alter_column(
        "order_items",
        "unit_price",
        type_=sa.Numeric(10, 2),
        existing_type=sa.Float(),
        postgresql_using="unit_price::numeric(10,2)",
    )
    op.alter_column(
        "payments",
        "amount",
        type_=sa.Numeric(10, 2),
        existing_type=sa.Float(),
        postgresql_using="amount::numeric(10,2)",
    )


def downgrade() -> None:
    op.alter_column(
        "orders",
        "total_amount",
        type_=sa.Float(),
        existing_type=sa.Numeric(10, 2),
    )
    op.alter_column(
        "order_items",
        "unit_price",
        type_=sa.Float(),
        existing_type=sa.Numeric(10, 2),
    )
    op.alter_column(
        "payments",
        "amount",
        type_=sa.Float(),
        existing_type=sa.Numeric(10, 2),
    )
