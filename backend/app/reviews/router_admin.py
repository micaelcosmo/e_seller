"""Rotas administrativas de avaliações: moderação e listagem."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.admin.audit import AdminAuditService
from app.core.db import get_session
from app.reviews.services import (
    InvalidModerationStatus,
    ReviewAdminLister,
    ReviewModerator,
    ReviewNotFound,
)
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/reviews", tags=["admin-reviews"])

require_staff = RequireRole("admin", "staff")


class ModerationIn(BaseModel):
    """Entrada para moderar uma avaliação."""

    status: str


def get_moderator(
    session: AsyncSession = Depends(get_session),
) -> ReviewModerator:
    """Monta o moderador de avaliações com a sessão injetada."""
    return ReviewModerator(session)


def get_admin_lister(
    session: AsyncSession = Depends(get_session),
) -> ReviewAdminLister:
    """Monta o listador de avaliações para admin com a sessão injetada."""
    return ReviewAdminLister(session)


@router.get("", dependencies=[Depends(require_staff)])
async def list_reviews_admin(
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    status: str | None = Query(default=None, description="Filtrar: pending/approved/rejected"),  # noqa: E501
    product_id: int | None = Query(default=None, description="Filtrar por ID do produto"),  # noqa: E501
    lister: ReviewAdminLister = Depends(get_admin_lister),
) -> Response:
    """Lista avaliações para o painel admin com paginação e X-Total-Count.

    Filtros: ?status=pending e ?product_id= (ambos opcionais, combináveis).
    """
    reviews = await lister.list_reviews(page, page_size, status, product_id)
    total = await lister.count_reviews(status, product_id)
    items = []
    for r in reviews:
        items.append({
            "id": r.id,
            "product_id": r.product_id,
            "user_id": r.user_id,
            "rating": r.rating,
            "comment": r.comment,
            "status": r.status.value,
            "created_at": str(r.created_at),
        })
    return Response(
        content=json.dumps(items),
        media_type="application/json",
        headers={"X-Total-Count": str(total)},
    )


@router.patch("/{review_id}/moderate")
async def moderate_review(
    review_id: int,
    data: ModerationIn,
    actor: User = Depends(require_staff),
    moderator: ReviewModerator = Depends(get_moderator),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Aplica o status de moderação a uma avaliação (approved ou rejected).

    Levanta 404 se o ID não existir; 422 se o status for inválido.
    Registra a ação no audit log.
    """
    try:
        review = await moderator.moderate(review_id, data.status)
    except ReviewNotFound as exc:
        raise HTTPException(
            status_code=404, detail="Avaliação não encontrada."
        ) from exc
    except InvalidModerationStatus as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Status inválido: {exc}. Use approved ou rejected.",
        ) from exc
    await AdminAuditService(session).log(
        actor_email=actor.email,
        action="moderate",
        resource_type="review",
        resource_id=str(review.id),
        detail=data.status,
    )
    return {"id": review.id, "status": review.status.value}
