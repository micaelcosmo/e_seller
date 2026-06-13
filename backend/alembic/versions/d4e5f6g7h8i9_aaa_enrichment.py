"""AAA enrichment: revoked_token, user_activity_log, api_key, user 2fa columns

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-06-13 06:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6g7h8i9"
down_revision: str | None = "c3d4e5f6g7h8"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona tabelas e colunas do épico AAA (blacklist, activity log, API Keys, TOTP)."""
    op.add_column(
        "user",
        sa.Column("totp_secret_enc", sa.String(512), nullable=True),
    )
    op.add_column(
        "user",
        sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_table(
        "revoked_token",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("jti", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_revoked_token_jti", "revoked_token", ["jti"], unique=True)

    op.create_table(
        "user_activity_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_activity_user_id", "user_activity_log", ["user_id"])
    op.create_index("ix_activity_event_type", "user_activity_log", ["event_type"])
    op.create_index("ix_activity_created_at", "user_activity_log", ["created_at"])
    op.create_index(
        "ix_activity_user_created",
        "user_activity_log",
        ["user_id", "created_at"],
    )

    op.create_table(
        "api_key",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("prefix", sa.String(16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_api_key_user_id", "api_key", ["user_id"])
    op.create_index("ix_api_key_key_hash", "api_key", ["key_hash"], unique=True)


def downgrade() -> None:
    """Remove tabelas e colunas do épico AAA."""
    op.drop_table("api_key")
    op.drop_index("ix_activity_user_created", table_name="user_activity_log")
    op.drop_index("ix_activity_created_at", table_name="user_activity_log")
    op.drop_index("ix_activity_event_type", table_name="user_activity_log")
    op.drop_index("ix_activity_user_id", table_name="user_activity_log")
    op.drop_table("user_activity_log")
    op.drop_index("ix_revoked_token_jti", table_name="revoked_token")
    op.drop_table("revoked_token")
    op.drop_column("user", "totp_enabled")
    op.drop_column("user", "totp_secret_enc")
