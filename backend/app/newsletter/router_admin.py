"""Rotas administrativas da newsletter: listar inscritos com paginação."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.newsletter.services import NewsletterAdminLister
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/newsletter", tags=["admin-newsletter"])

_require_staff = RequireRole("staff", "admin")


class SubscriberOut(BaseModel):
    """Dados de um inscrito para o painel administrativo."""

    id: int
    email: str
    active: bool
    created_at: str
    unsubscribed_at: str | None = None

    model_config = {"from_attributes": True}


def get_newsletter_admin_lister(
    session: AsyncSession = Depends(get_session),
) -> NewsletterAdminLister:
    """Monta o NewsletterAdminLister com a sessão injetada."""
    return NewsletterAdminLister(session)


@router.get("/stats", dependencies=[Depends(_require_staff)])
async def newsletter_stats(
    lister: NewsletterAdminLister = Depends(get_newsletter_admin_lister),
) -> dict:
    """Retorna estatísticas agregadas da newsletter: totais e novos nos últimos 30 dias.

    Campos: total_subscribers, active, inactive, new_last_30_days.
    """
    return await lister.get_stats()


@router.get("/subscribers", dependencies=[Depends(_require_staff)])
async def list_subscribers(
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    active: bool | None = Query(default=None, description="Filtrar por status ativo"),
    lister: NewsletterAdminLister = Depends(get_newsletter_admin_lister),
) -> Response:
    """Lista inscritos da newsletter com paginação e header X-Total-Count.

    Filtro opcional ?active=true/false para listar apenas ativos ou cancelados.
    """
    subscribers = await lister.list_subscribers(page, page_size, active)
    total = await lister.count_subscribers(active)
    items = []
    for sub in subscribers:
        out = SubscriberOut(
            id=sub.id,
            email=sub.email,
            active=sub.active,
            created_at=str(sub.created_at),
            unsubscribed_at=str(sub.unsubscribed_at) if sub.unsubscribed_at else None,
        )
        items.append(out.model_dump())
    return Response(
        content=json.dumps(items),
        media_type="application/json",
        headers={"X-Total-Count": str(total)},
    )
