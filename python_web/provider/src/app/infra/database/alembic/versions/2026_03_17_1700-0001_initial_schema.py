"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-17 17:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_sellers",
        sa.Column("supplier_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("identification_number", sa.String(length=50), nullable=False),
        sa.Column("legal_address", sa.String(length=255), nullable=False),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("bank_account_number", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "is_deleted", sa.Boolean(), nullable=True, server_default=sa.text("false")
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("identification_number"),
    )
    op.create_index("ix_platform_sellers_user_id", "platform_sellers", ["user_id"])
    op.execute(
        "SELECT setval(pg_get_serial_sequence('platform_sellers', 'supplier_id'), 10000000, false)"
    )

    op.create_table(
        "product_upload_tasks",
        sa.Column("task_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "supplier_id",
            sa.Integer(),
            sa.ForeignKey("platform_sellers.supplier_id"),
            nullable=False,
        ),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_product_upload_tasks_supplier_id", "product_upload_tasks", ["supplier_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_product_upload_tasks_supplier_id", table_name="product_upload_tasks"
    )
    op.drop_table("product_upload_tasks")
    op.drop_index("ix_platform_sellers_user_id", table_name="platform_sellers")
    op.drop_table("platform_sellers")
