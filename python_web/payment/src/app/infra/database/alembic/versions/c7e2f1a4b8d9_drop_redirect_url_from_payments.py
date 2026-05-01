"""drop redirect_url from payments

Revision ID: c7e2f1a4b8d9
Revises: 03925b9362d4
Create Date: 2026-04-16 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c7e2f1a4b8d9"
down_revision: Union[str, None] = "03925b9362d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("payments", "redirect_url")


def downgrade() -> None:
    op.add_column(
        "payments",
        sa.Column("redirect_url", sa.String(length=2048), nullable=True),
    )
