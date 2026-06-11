"""Ambiente do Alembic (síncrono): resolve a URL do banco e aplica migrations.

O app roda async (psycopg3/aiosqlite); o Alembic roda **síncrono** com a mesma
base de dados — psycopg3 suporta os dois modos. A URL vem de DATABASE_URL.
"""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Importa a Base e todos os models para que a metadata fique completa.
from app.core.db import Base
from app.catalog import models as _catalog_models  # noqa: F401
from app.delivery import models as _delivery_models  # noqa: F401
from app.orders import models as _orders_models  # noqa: F401
from app.payments import models as _payments_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _sync_database_url() -> str:
    """Retorna a URL do banco em modo síncrono (Alembic não usa async)."""
    url = os.environ.get("DATABASE_URL", "sqlite:///./e_seller.db")
    # Converte drivers async para o equivalente síncrono usado pelo Alembic.
    url = url.replace("sqlite+aiosqlite", "sqlite")
    url = url.replace("postgresql+asyncpg", "postgresql+psycopg")
    return url


def run_migrations_offline() -> None:
    """Executa migrations no modo offline (gera SQL sem conectar)."""
    context.configure(
        url=_sync_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrations conectando ao banco (modo online)."""
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = _sync_database_url()
    connectable = engine_from_config(
        section, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
