"""Rotas administrativas de entrega: reenvio de download."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import Clock
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.delivery.services import DownloadIssuer
from app.orders.models import Order, OrderItem, OrderStatus
from app.security.deps import RequireRole
from app.security.tokens import TokenFactory

router = APIRouter(prefix="/api/v1/admin/orders", tags=["admin-delivery"])

_require_staff = RequireRole("admin", "staff")


class GrantReissuer:
    """Emite novo grant de download para o primeiro item de um pedido (admin)."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        """Recebe sessão e configurações por injeção."""
        self.session = session
        self.settings = settings

    async def reissue_for_order(self, reference: str) -> str:
        """Busca o pedido pela referência e emite novo grant; retorna a URL.

        Levanta HTTPException 404 se o pedido não existir.
        Levanta HTTPException 422 se o pedido não estiver pago.
        """
        result = await self.session.scalars(
            select(Order).where(Order.reference == reference)
        )
        order = result.first()
        if order is None:
            raise HTTPException(status_code=404, detail="Pedido não encontrado.")
        if order.status != OrderStatus.PAID:
            raise HTTPException(
                status_code=422,
                detail="Reenvio só disponível para pedidos pagos.",
            )
        items_result = await self.session.scalars(
            select(OrderItem).where(OrderItem.order_id == order.id).limit(1)
        )
        item = items_result.first()
        if item is None:
            raise HTTPException(status_code=422, detail="Pedido sem itens.")
        issuer = DownloadIssuer(
            self.session,
            TokenFactory(),
            Clock(),
            ttl_days=self.settings.download_ttl_days,
            max_downloads=self.settings.download_max,
        )
        grant = await issuer.issue_for(item)
        return f"{self.settings.base_url}/api/v1/download/{grant.token}"


@router.post("/{reference}/resend-download")
async def resend_download(
    reference: str,
    _staff: object = Depends(_require_staff),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Emite novo link de download para o primeiro item de um pedido pago.

    Útil para suporte: cliente perdeu o link ou expirou.
    Retorna 404 se pedido não existir, 422 se não pago ou sem itens.
    """
    reissuer = GrantReissuer(session, settings)
    url = await reissuer.reissue_for_order(reference)
    return {"download_url": url}
