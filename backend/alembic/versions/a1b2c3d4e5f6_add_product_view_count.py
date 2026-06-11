"""add product view_count

Revision ID: a1b2c3d4e5f6
Revises: 3780bd0938d1
Create Date: 2026-06-10 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "3780bd0938d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona coluna view_count à tabela product (padrão 0)."""
    op.add_column(
        "product",
        sa.Column(
            "view_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    """Remove a coluna view_count da tabela product."""
    op.drop_column("product", "view_count")
