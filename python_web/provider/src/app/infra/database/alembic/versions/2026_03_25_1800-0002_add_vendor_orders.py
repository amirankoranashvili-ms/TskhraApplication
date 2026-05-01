"""add vendor orders

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-25 18:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vendor_orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column(
            "supplier_id",
            sa.Integer(),
            sa.ForeignKey("platform_sellers.supplier_id"),
            nullable=False,
        ),
        sa.Column("buyer_user_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PAID"),
        sa.Column("vendor_subtotal", sa.Float(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "order_id", "supplier_id", name="uq_vendor_order_per_supplier"
        ),
    )
    op.create_index("ix_vendor_orders_order_id", "vendor_orders", ["order_id"])
    op.create_index("ix_vendor_orders_supplier_id", "vendor_orders", ["supplier_id"])

    op.create_table(
        "vendor_order_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "vendor_order_id",
            sa.Uuid(),
            sa.ForeignKey("vendor_orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("product_title", sa.String(500), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("vendor_order_items")
    op.drop_index("ix_vendor_orders_supplier_id", "vendor_orders")
    op.drop_index("ix_vendor_orders_order_id", "vendor_orders")
    op.drop_table("vendor_orders")
