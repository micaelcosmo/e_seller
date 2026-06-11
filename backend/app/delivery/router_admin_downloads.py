"""Rotas administrativas de download grants: listagem com filtros."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.delivery.models import DownloadGrant
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/downloads", tags=["admin-downloads"])

_require_staff = RequireRole("admin", "staff")


class DownloadGrantAdminLister:
    """Lista DownloadGrants para administradores com filtros e paginação."""

    _PAGE_SIZE_MAX = 100

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    def _base_statement(
        self,
        product_id: int | None,
        expired: bool | None,
    ) -> object:
        """Constrói statement base com filtros opcionais."""
        stmt = select(DownloadGrant)
        if product_id is not None:
            stmt = stmt.where(DownloadGrant.product_id == product_id)
        if expired is True:
            stmt = stmt.where(DownloadGrant.expires_at < datetime.now(UTC))
        elif expired is False:
            stmt = stmt.where(DownloadGrant.expires_at >= datetime.now(UTC))
        return stmt

    async def list_grants(
        self,
        page: int,
        page_size: int,
        product_id: int | None = None,
        expired: bool | None = None,
    ) -> list[DownloadGrant]:
        """Retorna página de grants (mais recentes primeiro)."""
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = (
            self._base_statement(product_id, expired)
            .order_by(DownloadGrant.id.desc())
            .offset((page - 1) * effective_size)
            .limit(effective_size)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def count_grants(
        self,
        product_id: int | None = None,
        expired: bool | None = None,
    ) -> int:
        """Retorna o total de grants com os filtros aplicados."""
        base = self._base_statement(product_id, expired)
        count_stmt = select(func.count()).select_from(base.subquery())
        result = await self.session.scalar(count_stmt)
        return int(result or 0)


def get_lister(
    session: AsyncSession = Depends(get_session),
) -> DownloadGrantAdminLister:
    """Monta o DownloadGrantAdminLister com a sessão injetada."""
    return DownloadGrantAdminLister(session)


@router.get("", dependencies=[Depends(_require_staff)])
async def list_download_grants(
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    product_id: int | None = Query(default=None, description="Filtrar por produto"),
    expired: bool | None = Query(default=None, description="true=expirados, false=ativos"),  # noqa: E501
    lister: DownloadGrantAdminLister = Depends(get_lister),
) -> Response:
    """Lista DownloadGrants com paginação e filtros.

    Filtros opcionais: ?product_id= e ?expired=true|false.
    Retorna X-Total-Count com o total de registros para a query atual.
    """
    grants = await lister.list_grants(page, page_size, product_id, expired)
    total = await lister.count_grants(product_id, expired)
    items = []
    for g in grants:
        items.append({
            "id": g.id,
            "order_item_id": g.order_item_id,
            "product_id": g.product_id,
            "token": g.token,
            "expires_at": g.expires_at.isoformat() if g.expires_at else None,
            "max_downloads": g.max_downloads,
            "download_count": g.download_count,
            "created_at": g.created_at.isoformat() if g.created_at else None,
        })
    return Response(
        content=json.dumps(items),
        media_type="application/json",
        headers={"X-Total-Count": str(total)},
    )
