"""Infraestrutura de banco de dados ASSÍNCRONA: engine, sessões e base."""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

_logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base declarativa compartilhada por todos os models SQLAlchemy."""


class _BeforeExecuteListener:
    """Listener que marca o início de cada execução de query na conexão."""

    def __call__(
        self,
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ) -> None:
        """Empilha o timestamp de início no info da conexão."""
        conn.info.setdefault("query_start_time", []).append(time.monotonic())


class _AfterExecuteListener:
    """Listener que loga queries cujo tempo supera o limiar configurado."""

    def __init__(self, threshold_ms: int) -> None:
        """Recebe o limiar em milissegundos."""
        self.threshold_ms = threshold_ms

    def __call__(
        self,
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ) -> None:
        """Calcula o tempo e loga se ultrapassar o limiar."""
        start_times = conn.info.get("query_start_time", [])
        if not start_times:
            return
        elapsed_ms = (time.monotonic() - start_times.pop()) * 1000
        if elapsed_ms >= self.threshold_ms:
            _logger.warning(
                "Query lenta detectada",
                extra={
                    "elapsed_ms": round(elapsed_ms, 2),
                    "statement": statement[:500],
                },
            )


class Database:
    """Encapsula o engine async e a fábrica de sessões (sem estado global)."""

    def __init__(
        self,
        database_url: str,
        echo: bool = False,
        slow_query_ms: int = 0,
        pool_size: int = 10,
        pool_max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_pre_ping: bool = True,
    ) -> None:
        """Cria o engine assíncrono, a fábrica de sessões e listeners de obs.

        Os parâmetros de pool são ignorados para SQLite (NullPool implícito).
        """
        self.slow_query_ms = slow_query_ms
        is_sqlite = database_url.startswith("sqlite")
        engine_kwargs: dict = {"future": True, "echo": echo}
        if not is_sqlite:
            engine_kwargs["pool_size"] = pool_size
            engine_kwargs["max_overflow"] = pool_max_overflow
            engine_kwargs["pool_timeout"] = pool_timeout
            engine_kwargs["pool_pre_ping"] = pool_pre_ping
        self.engine = create_async_engine(database_url, **engine_kwargs)
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False
        )
        if slow_query_ms > 0:
            sync_engine = self.engine.sync_engine
            event.listen(sync_engine, "before_cursor_execute", _BeforeExecuteListener())
            event.listen(
                sync_engine,
                "after_cursor_execute",
                _AfterExecuteListener(slow_query_ms),
            )

    async def create_all(self) -> None:
        """Cria todas as tabelas registradas na metadata (uso em dev/test)."""
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    def create_session(self) -> AsyncSession:
        """Abre e retorna uma nova sessão assíncrona."""
        return self.session_factory()


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Dependency: entrega a sessão async, faz commit no sucesso e fecha."""
    database: Database = request.app.state.database
    session = database.create_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
