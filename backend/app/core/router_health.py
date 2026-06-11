"""Rota de healthcheck — liveness (/healthz) e readiness com DB (/health)."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.db import get_session

router = APIRouter(prefix="/api/v1", tags=["health"])
root_router = APIRouter(tags=["health"])


class HealthChecker:
    """Verifica liveness e conectividade com o banco de dados."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def check_db(self) -> str:
        """Executa SELECT 1 e retorna 'ok' ou 'error: <msg>'."""
        try:
            await self.session.execute(text("SELECT 1"))
            return "ok"
        except Exception as exc:
            return f"error: {exc}"


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Retorna liveness da aplicação (sem tocar no banco)."""
    return {"status": "ok"}


@router.get("/healthz/detail")
async def healthz_detail(
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    """Diagnóstico detalhado: status geral + saúde do banco (legado).

    Retorna sempre HTTP 200; usa campo 'ok' para lógica de alerta.
    """
    checker = HealthChecker(session)
    db_status = await checker.check_db()
    db_ok = db_status == "ok"
    checks: dict[str, object] = {"database": {"ok": db_ok}}
    if not db_ok:
        checks["database"] = {"ok": False, "error": db_status}
    return {"ok": db_ok, "checks": checks}


@root_router.get("/health/detail")
async def health_detail(
    request: Request,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> dict[str, object]:
    """Diagnóstico completo: versão, uptime, status do banco e do storage.

    Retorna sempre HTTP 200; use os campos individuais para detectar degradação.
    """
    checker = HealthChecker(session)
    db_status = await checker.check_db()
    storage_path = Path(settings.storage_dir)
    storage_ok = storage_path.exists() and storage_path.is_dir()
    started_at = getattr(request.app.state, "started_at", None)
    uptime = round(time.monotonic() - started_at, 1) if started_at is not None else None
    return {
        "version": settings.app_version,
        "uptime_seconds": uptime,
        "db_ok": db_status == "ok",
        "storage_ok": storage_ok,
    }


@root_router.get("/health")
async def health(
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    """Readiness check: pinga o banco e retorna 200 (saudável) ou 503 (degradado).

    Formato: {"status": "ok"|"degraded", "db": "ok"|"error: <msg>"}.
    """
    checker = HealthChecker(session)
    db_status = await checker.check_db()
    all_ok = db_status == "ok"
    return JSONResponse(
        content={"status": "ok" if all_ok else "degraded", "db": db_status},
        status_code=200 if all_ok else 503,
    )
