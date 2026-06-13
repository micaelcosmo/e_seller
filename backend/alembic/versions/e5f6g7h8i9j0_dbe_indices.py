"""DBE: índices compostos + GIN FTS funcional para PostgreSQL

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-06-13 08:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "e5f6g7h8i9j0"
down_revision: str | None = "d4e5f6g7h8i9"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona índices compostos no catálogo + índice GIN FTS (PostgreSQL only)."""
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    op.create_index("ix_product_status_featured", "product", ["status", "featured"])
    op.create_index("ix_order_user_status", "order", ["user_id", "status"])
    op.create_index("ix_order_reference_status", "order", ["reference", "status"])
    op.create_index(
        "ix_download_grant_order_expires",
        "download_grant",
        ["order_item_id", "expires_at"],
    )

    if is_pg:
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_product_fts_gin
            ON product
            USING GIN (
                to_tsvector(
                    'portuguese',
                    coalesce(title, '') || ' ' ||
                    coalesce(author, '') || ' ' ||
                    coalesce(description, '')
                )
            )
            """
        )


def downgrade() -> None:
    """Remove os índices adicionados no upgrade."""
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    if is_pg:
        op.execute("DROP INDEX IF EXISTS ix_product_fts_gin")

    op.drop_index("ix_download_grant_order_expires", table_name="download_grant")
    op.drop_index("ix_order_reference_status", table_name="order")
    op.drop_index("ix_order_user_status", table_name="order")
    op.drop_index("ix_product_status_featured", table_name="product")
