"""Rotas administrativas de estorno (refund), restritas a staff/admin."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import Clock
from app.core.db import get_session
from app.delivery.services import GrantRevoker
from app.entitlement.services import EntitlementService
from app.orders.services import OrderReader
from app.refunds.schemas import RefundIn, RefundOut
from app.refunds.services import RefundAdminLister, RefundService
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/refunds", tags=["refunds"])

require_staff = RequireRole("admin", "staff")


def get_refund_service(
    session: AsyncSession = Depends(get_session),
) -> RefundService:
    """Constrói o serviço de estorno com a sessão, a posse e os grants injetados."""
    return RefundService(
        session, EntitlementService(session), GrantRevoker(session, Clock())
    )


def get_order_reader(session: AsyncSession = Depends(get_session)) -> OrderReader:
    """Constrói o leitor de pedidos com a sessão injetada."""
    return OrderReader(session)


def get_refund_admin_lister(
    session: AsyncSession = Depends(get_session),
) -> RefundAdminLister:
    """Constrói o listador admin de estornos com a sessão injetada."""
    return RefundAdminLister(session)


@router.get("", response_model=list[RefundOut])
async def list_refunds_admin(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: object = Depends(require_staff),
    lister: RefundAdminLister = Depends(get_refund_admin_lister),
) -> object:
    """Lista estornos para administradores com paginação (mais recentes primeiro)."""
    return await lister.list_refunds(page, page_size)


@router.post("", response_model=RefundOut, status_code=201)
async def create_refund(
    data: RefundIn,
    _: object = Depends(require_staff),
    reader: OrderReader = Depends(get_order_reader),
    refunds: RefundService = Depends(get_refund_service),
) -> object:
    """Estorna (parcial ou totalmente) um pedido pago e revoga a posse.

    Levanta OrderNotFound (404), PaymentNotFound (409), InvalidTransition (409),
    RefundNotAllowed (422) via handler global de exceções de domínio.
    """
    order = await reader.get_by_reference(data.order_reference)
    return await refunds.refund_order(order, data.amount, data.reason)
