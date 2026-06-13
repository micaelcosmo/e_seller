"""Rotas /me: visão consolidada do usuário autenticado."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.cart.services import CartService
from app.core.db import get_session
from app.entitlement.services import EntitlementService
from app.orders.schemas import OrderOut
from app.orders.services import UserOrderLister
from app.security.deps import get_current_user
from app.wishlist.services import WishlistService

router = APIRouter(prefix="/api/v1/me", tags=["me"])


def get_order_lister(session: AsyncSession = Depends(get_session)) -> UserOrderLister:
    """Constrói o UserOrderLister com a sessão injetada."""
    return UserOrderLister(session)


def get_entitlement_service(
    session: AsyncSession = Depends(get_session),
) -> EntitlementService:
    """Constrói o EntitlementService com a sessão injetada."""
    return EntitlementService(session)


def get_wishlist_service(
    session: AsyncSession = Depends(get_session),
) -> WishlistService:
    """Constrói o WishlistService com a sessão injetada."""
    return WishlistService(session)


def get_cart_service(session: AsyncSession = Depends(get_session)) -> CartService:
    """Constrói o CartService com a sessão injetada."""
    return CartService(session)


@router.get("/orders", response_model=list[OrderOut])
async def me_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    status: str | None = Query(default=None, description="Filtrar por status"),
    user: User = Depends(get_current_user),
    lister: UserOrderLister = Depends(get_order_lister),
) -> list:
    """Lista os pedidos do usuário autenticado com paginação opcional."""
    return await lister.list_for_user(
        user_id=user.id,
        page=page,
        page_size=page_size,
        status=status,
    )


@router.get("/library")
async def me_library(
    user: User = Depends(get_current_user),
    entitlements: EntitlementService = Depends(get_entitlement_service),
) -> list:
    """Lista os e-books comprados pelo usuário autenticado (posse ativa)."""
    return await entitlements.library(user.id)


@router.get("/wishlist")
async def me_wishlist(
    user: User = Depends(get_current_user),
    wishlist: WishlistService = Depends(get_wishlist_service),
) -> list:
    """Lista os e-books na lista de desejos do usuário autenticado."""
    return await wishlist.items(user.id)


@router.get("/cart")
async def me_cart(
    user: User = Depends(get_current_user),
    cart: CartService = Depends(get_cart_service),
) -> list:
    """Lista os itens no carrinho do usuário autenticado."""
    return await cart.items(user.id)
