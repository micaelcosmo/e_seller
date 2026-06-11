"""Rotas de avaliações: listar (público) e criar (comprador verificado)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.core.db import get_session
from app.core.rate_limit import AuthAwareRateLimit
from app.reviews.schemas import ReviewIn, ReviewOut
from app.reviews.services import ReviewService
from app.security.deps import get_current_user

router = APIRouter(prefix="/api/v1/products/{slug}/reviews", tags=["reviews"])


def get_review_service(
    session: AsyncSession = Depends(get_session),
) -> ReviewService:
    """Monta o serviço de avaliações com a sessão injetada."""
    return ReviewService(session)


@router.get("", response_model=list[ReviewOut])
async def list_reviews(
    slug: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
    reviews: ReviewService = Depends(get_review_service),
) -> list:
    """Lista as avaliações públicas de um e-book com paginação."""
    return await reviews.list_for_product(slug, skip, limit)


_limit_review = AuthAwareRateLimit(max_requests=5, window_seconds=60)


@router.post("", response_model=ReviewOut, status_code=201)
async def create_review(
    slug: str,
    data: ReviewIn,
    user: User = Depends(get_current_user),
    reviews: ReviewService = Depends(get_review_service),
    _: None = Depends(_limit_review),
) -> ReviewOut:
    """Cria uma avaliação (apenas comprador verificado, 1 por e-book).

    Levanta InvalidRating (422), ReviewNotAllowed (403), AlreadyReviewed (409)
    via handler global de exceções de domínio.
    """
    review = await reviews.create(user.id, slug, data.rating, data.comment)
    return ReviewOut(
        id=review.id,
        rating=review.rating,
        comment=review.comment,
        author=user.email.split("@")[0],
        created_at=review.created_at.isoformat() if review.created_at else None,
    )
