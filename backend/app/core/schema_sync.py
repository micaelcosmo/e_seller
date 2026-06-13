"""Sincronização idempotente de colunas e índices novos no Postgres.

`create_all` cria tabelas novas, mas não altera tabelas já existentes. Quando
adicionamos colunas ou índices a uma tabela viva, aplicamos aqui ALTERs e
`CREATE INDEX IF NOT EXISTS` — ambos idempotentes no Postgres.
No SQLite (testes) as colunas já nascem do `create_all`, então a sincronização
é ignorada.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class SchemaSync:
    """Garante a existência de colunas e índices novos em tabelas já criadas."""

    def __init__(self, engine: AsyncEngine) -> None:
        """Recebe o engine async e prepara as listas de mudanças a garantir."""
        self.engine = engine

        # (tabela, coluna, definição SQL) — idempotente via ADD COLUMN IF NOT EXISTS.
        # Aspas duplas nos nomes de tabela: "order" é palavra reservada.
        self.expected_columns: list[tuple[str, str, str]] = [
            ("product", "publisher_id", "INTEGER REFERENCES publisher(id)"),
            ("product", "series_id", "INTEGER REFERENCES series(id)"),
            ("product", "view_count", "INTEGER DEFAULT 0 NOT NULL"),
            ("product", "featured", "BOOLEAN DEFAULT false NOT NULL"),
            ("order", "billing_profile_id", "INTEGER REFERENCES billing_profile(id)"),
            ("order", "updated_at", "TIMESTAMPTZ DEFAULT NOW()"),
            ("user", "deleted_at", "TIMESTAMPTZ"),
            ("user", "totp_secret_enc", "VARCHAR(512)"),
            ("user", "totp_enabled", "BOOLEAN DEFAULT false NOT NULL"),
        ]

        # (nome do índice, tabela, coluna) — idempotente via CREATE INDEX IF NOT EXISTS.
        self.expected_indexes: list[tuple[str, str, str]] = [
            ("ix_order_item_order_id", "order_item", "order_id"),
            ("ix_order_item_product_id", "order_item", "product_id"),
            ("ix_payment_order_id", "payment", "order_id"),
            ("ix_payment_status", "payment", "status"),
            ("ix_download_grant_order_item_id", "download_grant", "order_item_id"),
            ("ix_download_grant_product_id", "download_grant", "product_id"),
            ("ix_download_log_grant_id", "download_log", "download_grant_id"),
            ("ix_review_user_id", "review", "user_id"),
            ("ix_category_slug", "category", "slug"),
        ]

    async def run(self) -> None:
        """Aplica ALTERs e índices idempotentes; só faz sentido no dialeto Postgres."""
        if self.engine.dialect.name != "postgresql":
            return
        async with self.engine.begin() as connection:
            for table, column, definition in self.expected_columns:
                statement = text(
                    f'ALTER TABLE "{table}" '
                    f"ADD COLUMN IF NOT EXISTS {column} {definition}"
                )
                await connection.execute(statement)
            for index_name, table, column in self.expected_indexes:
                statement = text(
                    f'CREATE INDEX IF NOT EXISTS "{index_name}" '
                    f'ON "{table}"({column})'
                )
                await connection.execute(statement)
