"""Rota de healthcheck — liveness (/healthz) e readiness com DB (/health)."""

from __future__ import annotations

import shutil
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
    """Verifica liveness, latência do banco e espaço em disco."""

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

    async def db_latency_ms(self) -> float | None:
        """Mede a latência do SELECT 1 em milissegundos; None se falhar."""
        try:
            start = time.monotonic()
            await self.session.execute(text("SELECT 1"))
            return round((time.monotonic() - start) * 1000, 2)
        except Exception:
            return None

    @staticmethod
    def disk_free_mb(path: str) -> float | None:
        """Retorna espaço livre em MB no path; None se inacessível."""
        try:
            usage = shutil.disk_usage(path)
            return round(usage.free / (1024 * 1024), 1)
        except Exception:
            return None


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Retorna liveness da aplicação (sem tocar no banco)."""
    return {"status": "ok"}


@router.get("/healthz/detail")
async def healthz_detail(
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> dict[str, object]:
    """Diagnóstico detalhado: status geral + latência do banco + disco.

    Retorna sempre HTTP 200; usa campo 'ok' para lógica de alerta.
    """
    checker = HealthChecker(session)
    latency = await checker.db_latency_ms()
    db_ok = latency is not None
    disk = checker.disk_free_mb(settings.storage_dir)
    checks: dict[str, object] = {
        "database": {"ok": db_ok, "latency_ms": latency},
        "disk": {"free_mb": disk},
    }
    return {"ok": db_ok, "checks": checks}


@root_router.get("/health/detail")
async def health_detail(
    request: Request,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> dict[str, object]:
    """Diagnóstico completo: versão, uptime, latência DB, disco e storage.

    Retorna sempre HTTP 200; use os campos individuais para detectar degradação.
    """
    checker = HealthChecker(session)
    latency = await checker.db_latency_ms()
    db_ok = latency is not None
    storage_path = Path(settings.storage_dir)
    storage_ok = storage_path.exists() and storage_path.is_dir()
    started_at = getattr(request.app.state, "started_at", None)
    uptime = round(time.monotonic() - started_at, 1) if started_at is not None else None
    disk = checker.disk_free_mb(settings.storage_dir)
    return {
        "version": settings.app_version,
        "uptime_seconds": uptime,
        "db_ok": db_ok,
        "db_latency_ms": latency,
        "disk_free_mb": disk,
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
