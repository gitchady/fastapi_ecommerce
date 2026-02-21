"""Add product rating and timestamps

Revision ID: 5985f80d4af0
Revises: de236a0f1802
Create Date: 2026-02-21 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5985f80d4af0"
down_revision: Union[str, Sequence[str], None] = "de236a0f1802"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "rating",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "updated_at")
    op.drop_column("products", "created_at")
    op.drop_column("products", "rating")
