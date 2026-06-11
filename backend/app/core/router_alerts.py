"""Endpoint /alerts/check: verifica condições de alerta operacional."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.orders.models import Order, OrderStatus
from app.payments.models import Payment
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/alerts", tags=["alerts"])

require_staff = RequireRole("admin", "staff")

# Limiar: erros de pagamento (rejected) em % do total.
_ERROR_RATE_THRESHOLD_PCT = 20.0

# Valores de status que indicam falha no provedor.
_FAILED_STATUSES = ("rejected", "cancelled", "failed")


class AlertChecker:
    """Verifica condições de alerta operacional no banco de dados."""

    def __init__(
        self,
        session: AsyncSession,
        email_fail_count: int = 0,
    ) -> None:
        """Recebe sessão e contador de falhas de e-mail por injeção."""
        self.session = session
        self.email_fail_count = email_fail_count

    async def check(self) -> dict:
        """Executa todas as verificações e retorna o estado de cada alerta."""
        alerts = []
        orphan_count = await self._orphan_paid_orders()
        if orphan_count > 0:
            alerts.append(
                {
                    "name": "pagamentos_sem_entrega",
                    "severity": "alta",
                    "detail": (
                        f"{orphan_count} pedido(s) pago(s) "
                        "sem grant de download."
                    ),
                }
            )

        error_rate = await self._payment_error_rate()
        if error_rate > _ERROR_RATE_THRESHOLD_PCT:
            alerts.append(
                {
                    "name": "taxa_erro_pagamento",
                    "severity": "alta",
                    "detail": (
                        f"Taxa de erro de pagamento: {error_rate:.1f}% "
                        f"(limiar: {_ERROR_RATE_THRESHOLD_PCT}%)."
                    ),
                }
            )

        if self.email_fail_count > 0:
            alerts.append(
                {
                    "name": "falhas_email",
                    "severity": "media",
                    "detail": (
                        f"{self.email_fail_count} falha(s) de envio de e-mail "
                        "acumulada(s) desde o último restart."
                    ),
                }
            )

        low_grant_count = await self._low_download_grants()
        if low_grant_count > 0:
            alerts.append(
                {
                    "name": "estoque_downloads_baixo",
                    "severity": "media",
                    "detail": (
                        f"{low_grant_count} grant(s) de download com "
                        "1 ou nenhum download restante."
                    ),
                }
            )

        return {
            "ok": len(alerts) == 0,
            "alerts": alerts,
        }

    async def _orphan_paid_orders(self) -> int:
        """Conta pedidos PAID sem grant de download (via order_item)."""
        from app.delivery.models import DownloadGrant
        from app.orders.models import OrderItem

        # Subquery: order_ids que têm pelo menos um DownloadGrant.
        grant_subq = (
            select(OrderItem.order_id)
            .join(DownloadGrant, DownloadGrant.order_item_id == OrderItem.id)
            .distinct()
            .scalar_subquery()
        )
        result = await self.session.scalar(
            select(func.count())
            .select_from(Order)
            .where(
                Order.status == OrderStatus.PAID,
                Order.id.notin_(grant_subq),
            )
        )
        return int(result or 0)

    async def _low_download_grants(self) -> int:
        """Conta grants de download com 1 ou nenhum download restante."""
        from app.delivery.models import DownloadGrant

        result = await self.session.scalar(
            select(func.count())
            .select_from(DownloadGrant)
            .where(
                (DownloadGrant.max_downloads - DownloadGrant.download_count) <= 1
            )
        )
        return int(result or 0)

    async def _payment_error_rate(self) -> float:
        """Retorna a porcentagem de pagamentos em estado de erro vs total."""
        total = await self.session.scalar(
            select(func.count()).select_from(Payment)
        )
        if not total:
            return 0.0
        failed = await self.session.scalar(
            select(func.count())
            .select_from(Payment)
            .where(Payment.status.in_(list(_FAILED_STATUSES)))
        )
        return round(float(failed or 0) / float(total) * 100, 1)


@router.get("/check")
async def check_alerts(
    request: Request,
    session: AsyncSession = Depends(get_session),
    _staff: object = Depends(require_staff),
) -> dict:
    """Verifica condições de alerta operacional (requer staff/admin).

    Retorna ok=true se nenhum alerta ativo; ok=false com lista de alertas.
    Inclui contagem de falhas de e-mail do EmailFailCounter em app.state.
    """
    counter = getattr(request.app.state, "email_fail_counter", None)
    email_fail_count = counter.count if counter is not None else 0
    return await AlertChecker(session, email_fail_count).check()
