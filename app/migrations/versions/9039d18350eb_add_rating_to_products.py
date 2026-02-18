"""add rating to products

Revision ID: 9039d18350eb
Revises: 51a913aadae5
Create Date: 2026-02-18 11:27:32.174148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9039d18350eb'
down_revision: Union[str, Sequence[str], None] = '51a913aadae5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "products",
        sa.Column(
            "rating",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("products", "rating")
