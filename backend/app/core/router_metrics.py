"""Endpoint /metrics: KPIs operacionais e de negócio (somente staff/admin)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.catalog.models import Product, ProductStatus
from app.core.db import get_session
from app.orders.models import Order, OrderStatus
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

require_staff = RequireRole("admin", "staff")


class MetricsCollector:
    """Coleta KPIs operacionais e de negócio em uma única consulta assíncrona."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def collect(self) -> dict:
        """Executa consultas no banco e retorna o dicionário de métricas."""
        total_products = await self._count(Product)
        published_products = await self._count_where(
            Product, Product.status == ProductStatus.PUBLISHED
        )
        total_users = await self._count(User)
        active_users = await self._count_where(User, User.is_active == True)  # noqa: E712
        total_orders = await self._count(Order)
        paid_orders = await self._count_where(
            Order, Order.status == OrderStatus.PAID
        )
        revenue_result = await self.session.scalar(
            select(func.sum(Order.amount)).where(Order.status == OrderStatus.PAID)
        )
        revenue = float(revenue_result or 0)
        return {
            "products": {
                "total": total_products,
                "published": published_products,
                "draft": total_products - published_products,
            },
            "users": {
                "total": total_users,
                "active": active_users,
            },
            "orders": {
                "total": total_orders,
                "paid": paid_orders,
                "conversion_pct": (
                    round(paid_orders / total_orders * 100, 1)
                    if total_orders
                    else 0.0
                ),
            },
            "revenue": {
                "total_brl": round(revenue, 2),
            },
        }

    async def _count(self, model) -> int:
        """Conta todos os registros de um model."""
        result = await self.session.scalar(select(func.count()).select_from(model))
        return int(result or 0)

    async def _count_where(self, model, condition) -> int:
        """Conta registros de um model com condição."""
        result = await self.session.scalar(
            select(func.count()).select_from(model).where(condition)
        )
        return int(result or 0)


class PrometheusFormatter:
    """Serializa um dict de métricas no formato Prometheus text exposition."""

    _CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"

    def format(self, data: dict) -> str:
        """Converte o dicionário de métricas em linhas Prometheus."""
        lines: list[str] = []
        self._flat(lines, data, prefix="eseller")
        return "\n".join(lines) + "\n"

    def _flat(self, lines: list[str], node: dict, prefix: str) -> None:
        """Percorre o dict recursivamente emitindo linhas HELP/TYPE/valor."""
        for key, value in node.items():
            full_name = f"{prefix}_{key}"
            if isinstance(value, dict):
                self._flat(lines, value, full_name)
            else:
                lines.append(f"# TYPE {full_name} gauge")
                lines.append(f"{full_name} {value}")


@router.get("")
async def get_metrics(
    session: AsyncSession = Depends(get_session),
    _staff: object = Depends(require_staff),
) -> dict:
    """Retorna KPIs operacionais em JSON (requer papel staff ou admin)."""
    return await MetricsCollector(session).collect()


@router.get("/prometheus")
async def get_metrics_prometheus(
    session: AsyncSession = Depends(get_session),
    _staff: object = Depends(require_staff),
) -> Response:
    """Retorna KPIs operacionais no formato Prometheus text exposition."""
    data = await MetricsCollector(session).collect()
    text = PrometheusFormatter().format(data)
    return Response(
        content=text,
        media_type=PrometheusFormatter._CONTENT_TYPE,
    )
