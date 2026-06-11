"""add review status for moderation

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-11 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b2c3d4e5f6g7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona coluna status à tabela review (padrão pending)."""
    op.add_column(
        "review",
        sa.Column(
            "status",
            sa.Enum("pending", "approved", "rejected", name="reviewstatus"),
            nullable=False,
            server_default="pending",
        ),
    )


def downgrade() -> None:
    """Remove a coluna status da tabela review."""
    op.drop_column("review", "status")
    op.execute("DROP TYPE IF EXISTS reviewstatus")
