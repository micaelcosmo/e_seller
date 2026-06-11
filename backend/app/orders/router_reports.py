"""Rotas de relatórios administrativos de vendas."""

from __future__ import annotations

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.orders.models import Order, OrderItem, OrderStatus
from app.orders.services import TopProductsService
from app.security.deps import RequireRole

router = APIRouter(prefix="/api/v1/admin/reports", tags=["admin-reports"])

require_staff = RequireRole("admin", "staff")


class SalesReportService:
    """Gera relatórios de vendas por período a partir dos pedidos pagos."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def sales_by_period(
        self, date_from: date, date_to: date
    ) -> dict:
        """Retorna pedidos pagos, receita e top produtos no período."""
        start = datetime(date_from.year, date_from.month, date_from.day, tzinfo=UTC)
        end = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59, tzinfo=UTC)

        # Total de pedidos e receita no período.
        row = await self.session.execute(
            select(func.count(Order.id), func.sum(Order.amount)).where(
                Order.status == OrderStatus.PAID,
                Order.created_at >= start,
                Order.created_at <= end,
            )
        )
        count, revenue = row.one()
        revenue = float(revenue or 0)

        # Top 10 produtos por unidades vendidas.
        top_rows = await self.session.execute(
            select(
                OrderItem.product_id,
                func.count(OrderItem.id).label("units"),
                func.sum(OrderItem.unit_price).label("revenue"),
            )
            .join(Order, OrderItem.order_id == Order.id)
            .where(
                Order.status == OrderStatus.PAID,
                Order.created_at >= start,
                Order.created_at <= end,
            )
            .group_by(OrderItem.product_id)
            .order_by(func.count(OrderItem.id).desc())
            .limit(10)
        )
        top_products = []
        for top_row in top_rows:
            top_products.append({
                "product_id": top_row.product_id,
                "units_sold": top_row.units,
                "revenue_brl": round(float(top_row.revenue or 0), 2),
            })

        return {
            "period": {
                "from": str(date_from),
                "to": str(date_to),
            },
            "orders_paid": int(count or 0),
            "revenue_brl": round(revenue, 2),
            "top_products": top_products,
        }


@router.get("/orders/summary")
async def orders_summary(
    session: AsyncSession = Depends(get_session),
    _staff: object = Depends(require_staff),
) -> dict:
    """Retorna contagem de pedidos agrupados por status.

    Útil para o dashboard administrativo ver a distribuição dos estados dos pedidos.
    """
    from sqlalchemy import func

    rows = await session.execute(
        select(Order.status, func.count(Order.id).label("count"))
        .group_by(Order.status)
    )
    result = {row.status.value: row.count for row in rows.all()}
    for status in OrderStatus:
        result.setdefault(status.value, 0)
    return result


@router.get("/top-products")
async def top_products_report(
    limit: int = Query(default=10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
    _staff: object = Depends(require_staff),
) -> list:
    """Retorna os produtos mais vendidos (por volume de itens em pedidos pagos)."""
    return await TopProductsService(session).top_products(limit)


@router.get("/sales")
async def sales_report(
    date_from: date = Query(description="Início do período (YYYY-MM-DD)"),
    date_to: date = Query(description="Fim do período (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session),
    _staff: object = Depends(require_staff),
) -> dict:
    """Retorna relatório de vendas pagas no período; requer staff ou admin."""
    return await SalesReportService(session).sales_by_period(date_from, date_to)
