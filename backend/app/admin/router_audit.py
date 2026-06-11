"""Rotas administrativas do audit log: listagem de ações de escrita."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.audit import AdminAuditLog
from app.core.db import get_session
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/audit-log", tags=["admin-audit"])

_require_staff = RequireRole("staff", "admin")


class AdminAuditReader:
    """Lê e pagina entradas do audit log administrativo."""

    _PAGE_SIZE_MAX = 100

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção de dependência."""
        self.session = session

    def _base_statement(
        self,
        actor: str | None,
        action: str | None,
        resource_type: str | None,
    ) -> object:
        """Constrói statement base com filtros opcionais."""
        stmt = select(AdminAuditLog)
        if actor:
            stmt = stmt.where(AdminAuditLog.actor_email == actor)
        if action:
            stmt = stmt.where(AdminAuditLog.action == action)
        if resource_type:
            stmt = stmt.where(AdminAuditLog.resource_type == resource_type)
        return stmt

    async def list_entries(
        self,
        page: int,
        page_size: int,
        actor: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> list[AdminAuditLog]:
        """Retorna página de entradas do audit log (mais recentes primeiro)."""
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = (
            self._base_statement(actor, action, resource_type)
            .order_by(AdminAuditLog.id.desc())
            .offset((page - 1) * effective_size)
            .limit(effective_size)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def count_entries(
        self,
        actor: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> int:
        """Retorna total de entradas com os filtros aplicados."""
        from sqlalchemy import func as sa_func

        base = self._base_statement(actor, action, resource_type)
        count_stmt = select(sa_func.count()).select_from(base.subquery())
        result = await self.session.scalar(count_stmt)
        return int(result or 0)


def get_audit_reader(
    session: AsyncSession = Depends(get_session),
) -> AdminAuditReader:
    """Monta o leitor do audit log com a sessão injetada."""
    return AdminAuditReader(session)


@router.get("", dependencies=[Depends(_require_staff)])
async def list_audit_log(
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    actor: str | None = Query(default=None, description="Filtrar por e-mail do ator"),
    action: str | None = Query(default=None, description="Filtrar por ação"),
    resource_type: str | None = Query(
        default=None, description="Filtrar por tipo de recurso"
    ),
    reader: AdminAuditReader = Depends(get_audit_reader),
) -> Response:
    """Lista entradas do audit log administrativo com paginação e filtros.

    Filtros: ?actor=email&action=create&resource_type=coupon.
    Retorna X-Total-Count com o total de entradas (sem paginação).
    """
    entries = await reader.list_entries(
        page, page_size, actor, action, resource_type
    )
    total = await reader.count_entries(actor, action, resource_type)
    items = []
    for entry in entries:
        items.append({
            "id": entry.id,
            "actor_email": entry.actor_email,
            "action": entry.action,
            "resource_type": entry.resource_type,
            "resource_id": entry.resource_id,
            "detail": entry.detail,
            "created_at": str(entry.created_at),
        })
    return Response(
        content=json.dumps(items),
        media_type="application/json",
        headers={"X-Total-Count": str(total)},
    )
