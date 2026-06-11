"""Rotas da lista de desejos (wishlist), todas autenticadas."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.catalog.schemas import ProductListItem
from app.core.db import get_session
from app.security.deps import get_current_user
from app.wishlist.services import WishlistService

router = APIRouter(prefix="/api/v1/wishlist", tags=["wishlist"])


def get_wishlist_service(
    session: AsyncSession = Depends(get_session),
) -> WishlistService:
    """Monta o serviço de wishlist com a sessão injetada."""
    return WishlistService(session)


@router.get("", response_model=list[ProductListItem])
async def list_wishlist(
    user: User = Depends(get_current_user),
    wishlist: WishlistService = Depends(get_wishlist_service),
) -> list:
    """Lista os e-books na lista de desejos do usuário."""
    return await wishlist.items(user.id)


@router.post("/{slug}", status_code=204)
async def add_to_wishlist(
    slug: str,
    user: User = Depends(get_current_user),
    wishlist: WishlistService = Depends(get_wishlist_service),
) -> None:
    """Adiciona um e-book à lista de desejos.

    Levanta WishlistProductNotFound (404) via handler global.
    """
    await wishlist.add(user.id, slug)


@router.delete("/{slug}", status_code=204)
async def remove_from_wishlist(
    slug: str,
    user: User = Depends(get_current_user),
    wishlist: WishlistService = Depends(get_wishlist_service),
) -> None:
    """Remove um e-book da lista de desejos.

    Levanta WishlistProductNotFound (404) via handler global.
    """
    await wishlist.remove(user.id, slug)
