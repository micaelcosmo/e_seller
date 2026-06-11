"""Rotas de pedidos (API JSON)."""

from __future__ import annotations

import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.catalog.services import ProductCatalog
from app.core.clock import Clock
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.coupons.services import CouponService
from app.orders.schemas import OrderAdminDetailOut, OrderCreateIn, OrderOut
from app.orders.services import (
    OrderAdminLister,
    OrderCancellationNotAllowed,
    OrderCanceller,
    OrderCreator,
    OrderReader,
    UserOrderLister,
)
from app.payments.gateways import FakePaymentGateway
from app.payments.services import CheckoutService
from app.security.deps import RequireRole, get_current_user, get_optional_user

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


def get_order_creator(
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> OrderCreator:
    """Monta o OrderCreator com catálogo, checkout (gateway fake) e cupons."""
    catalog = ProductCatalog(session)
    gateway = FakePaymentGateway(settings.base_url)
    checkout = CheckoutService(gateway)
    coupons = CouponService(session, Clock())
    return OrderCreator(session, catalog, checkout, coupons)


def get_order_reader(session: AsyncSession = Depends(get_session)) -> OrderReader:
    """Monta o OrderReader com a sessão injetada."""
    return OrderReader(session)


def get_order_admin_lister(
    session: AsyncSession = Depends(get_session),
) -> OrderAdminLister:
    """Monta o OrderAdminLister com a sessão injetada."""
    return OrderAdminLister(session)


def get_user_order_lister(
    session: AsyncSession = Depends(get_session),
) -> UserOrderLister:
    """Monta o UserOrderLister com a sessão injetada."""
    return UserOrderLister(session)


def get_order_canceller(
    session: AsyncSession = Depends(get_session),
) -> OrderCanceller:
    """Monta o OrderCanceller com a sessão injetada."""
    return OrderCanceller(session)


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    data: OrderCreateIn,
    creator: OrderCreator = Depends(get_order_creator),
    user: User | None = Depends(get_optional_user),
) -> object:
    """Cria um pedido pendente; vincula à conta se o comprador estiver logado.

    Levanta ProductNotFound (404) ou CouponInvalid (422) via handler global.
    """
    user_id = user.id if user is not None else None
    return await creator.create(
        data.product_slug, data.buyer_email, user_id, data.coupon_code
    )


@router.post("/my/{reference}/cancel", response_model=OrderOut)
async def cancel_order(
    reference: str,
    user: User = Depends(get_current_user),
    canceller: OrderCanceller = Depends(get_order_canceller),
) -> object:
    """Cancela um pedido PENDING do comprador autenticado.

    Retorna 409 se o pedido não puder ser cancelado (já pago ou já cancelado).
    Retorna 404 se a referência não existir ou não pertencer ao usuário.
    """
    try:
        return await canceller.cancel(reference, user.id)
    except OrderCancellationNotAllowed as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Pedido não pode ser cancelado (status: {exc}).",
        ) from exc


@router.get("/my", response_model=list[OrderOut])
async def list_my_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    status: str | None = Query(default=None, description="Filtrar por status"),
    user: User = Depends(get_current_user),
    lister: UserOrderLister = Depends(get_user_order_lister),
) -> object:
    """Lista os pedidos do usuário autenticado (mais recentes primeiro).

    Requer autenticação; retorna lista vazia se não houver pedidos.
    Filtro opcional ?status= (pending, paid, failed, cancelled, refunded).
    """
    return await lister.list_for_user(user.id, page, page_size, status)


_require_staff = RequireRole("staff", "admin")


@router.get("/export", dependencies=[Depends(_require_staff)])
async def export_orders_csv(
    status: str | None = Query(default=None, description="Filtrar por status"),
    date_from: str | None = Query(default=None, description="Data inicial ISO 8601"),
    date_to: str | None = Query(default=None, description="Data final ISO 8601"),
    lister: OrderAdminLister = Depends(get_order_admin_lister),
) -> StreamingResponse:
    """Exporta pedidos como CSV para download.

    Colunas: reference, buyer_email, amount, status, created_at.
    Suporta os mesmos filtros de status e data da listagem admin.
    """
    orders = await lister.list_orders(
        status, page=1, page_size=10000, date_from=date_from, date_to=date_to
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["reference", "buyer_email", "amount", "status", "created_at"])
    for order in orders:
        writer.writerow([
            order.reference,
            order.buyer_email,
            str(order.amount),
            order.status.value,
            order.created_at.isoformat() if order.created_at else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.read()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=orders.csv",
            "X-Export-Limit": "10000",
        },
    )


@router.get("/{reference}", response_model=OrderOut)
async def get_order(
    reference: str,
    reader: OrderReader = Depends(get_order_reader),
) -> object:
    """Retorna o status de um pedido pela referência pública (404 se não encontrado)."""
    return await reader.get_by_reference(reference)


@router.get("/admin/{reference}", response_model=OrderAdminDetailOut)
async def get_order_admin(
    reference: str,
    _staff: object = Depends(_require_staff),
    reader: OrderReader = Depends(get_order_reader),
) -> object:
    """Retorna dados completos de um pedido (com itens) para o painel administrativo.

    Levanta 404 via handler global se a referência não existir.
    """
    return await reader.get_by_reference(reference)


@router.get(
    "",
    dependencies=[Depends(_require_staff)],
)
async def list_orders_admin(
    status: str | None = Query(default=None, description="Filtrar por status"),
    q: str | None = Query(default=None, description="Filtrar por e-mail do comprador"),
    buyer_email: str | None = Query(  # noqa: E501
        default=None, description="Busca parcial case-insensitive no e-mail"
    ),
    ref: str | None = Query(default=None, description="Buscar por referência exata"),
    date_from: str | None = Query(default=None, description="Data inicial ISO 8601"),
    date_to: str | None = Query(default=None, description="Data final ISO 8601"),
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    lister: OrderAdminLister = Depends(get_order_admin_lister),
) -> Response:
    """Lista pedidos para administradores com paginação, filtros e total no header.

    Retorna X-Total-Count com o número total de pedidos para a query atual.
    Suporta filtros ?date_from= e ?date_to= (ISO 8601: 2026-01-01).
    ?buyer_email= e ?q= fazem busca parcial case-insensitive no e-mail do comprador.
    """
    email_filter = buyer_email or q
    orders = await lister.list_orders(
        status, page, page_size, email_filter, ref, date_from, date_to
    )
    total = await lister.count_orders(status, email_filter, ref, date_from, date_to)
    schemas = [OrderOut.model_validate(o) for o in orders]
    return Response(
        content=json.dumps([s.model_dump() for s in schemas], default=str),
        media_type="application/json",
        headers={"X-Total-Count": str(total)},
    )
