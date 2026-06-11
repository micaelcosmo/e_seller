"""Rotas do carrinho: listar, adicionar, remover e finalizar (checkout)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.cart.services import CartService
from app.catalog.schemas import ProductListItem
from app.core.db import get_session
from app.orders.router import get_order_creator
from app.orders.schemas import OrderOut
from app.orders.services import OrderCreator
from app.security.deps import get_current_user

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


class CheckoutIn(BaseModel):
    """Entrada do checkout do carrinho (cupom opcional)."""

    coupon_code: str | None = None


def get_cart_service(
    session: AsyncSession = Depends(get_session),
) -> CartService:
    """Monta o serviço de carrinho com a sessão injetada."""
    return CartService(session)


@router.get("", response_model=list[ProductListItem])
async def list_cart(
    user: User = Depends(get_current_user),
    cart: CartService = Depends(get_cart_service),
) -> list:
    """Lista os itens do carrinho do usuário."""
    return await cart.items(user.id)


@router.post("/checkout", response_model=OrderOut, status_code=201)
async def checkout(
    data: CheckoutIn,
    user: User = Depends(get_current_user),
    cart: CartService = Depends(get_cart_service),
    creator: OrderCreator = Depends(get_order_creator),
) -> object:
    """Finaliza o carrinho: cria um pedido com todos os itens e o esvazia.

    Levanta CouponInvalid (422) via handler global; carrinho permanece intacto
    caso o checkout falhe.
    """
    products = await cart.items(user.id)
    if not products:
        raise HTTPException(status_code=400, detail="Carrinho vazio")
    order = await creator.create_from_items(
        user.email, products, user.id, data.coupon_code
    )
    await cart.clear(user.id)
    return order


@router.post("/{slug}", status_code=204)
async def add_to_cart(
    slug: str,
    user: User = Depends(get_current_user),
    cart: CartService = Depends(get_cart_service),
) -> None:
    """Adiciona um e-book ao carrinho.

    Levanta CartProductNotFound (404) ou AlreadyOwned (409) via handler global.
    """
    await cart.add(user.id, slug)


@router.delete("/{slug}", status_code=204)
async def remove_from_cart(
    slug: str,
    user: User = Depends(get_current_user),
    cart: CartService = Depends(get_cart_service),
) -> None:
    """Remove um e-book do carrinho.

    Levanta CartProductNotFound (404) via handler global.
    """
    await cart.remove(user.id, slug)
