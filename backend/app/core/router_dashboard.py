"""Endpoint /dashboard: dados de evolução do projeto para o painel de relatório."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

# Caminho do backlog.json montado via volume no Docker (ou variável de ambiente).
_BACKLOG_PATH = Path(os.environ.get("BACKLOG_PATH", "/app/report/backlog.json"))


class DashboardDataService:
    """Lê o backlog.json e gera métricas de evolução do projeto."""

    def __init__(self, backlog_path: Path) -> None:
        """Recebe o caminho do arquivo de backlog."""
        self.backlog_path = backlog_path

    def collect(self) -> dict:
        """Retorna métricas de progresso derivadas do backlog.json."""
        if not self.backlog_path.is_file():
            return {"error": "backlog.json não encontrado", "tasks": {}}
        data = json.loads(self.backlog_path.read_text(encoding="utf-8"))
        tasks = data.get("tasks", [])
        by_state: dict[str, int] = {}
        by_area: dict[str, dict[str, int]] = {}
        for task in tasks:
            state = task.get("state", "unknown")
            area = task.get("area", "Sem área")
            by_state[state] = by_state.get(state, 0) + 1
            if area not in by_area:
                by_area[area] = {}
            by_area[area][state] = by_area[area].get(state, 0) + 1
        total = len(tasks)
        done = by_state.get("done", 0)
        return {
            "project": data.get("project", "e_seller"),
            "updated": data.get("updated", ""),
            "total_tasks": total,
            "done": done,
            "backlog": by_state.get("backlog", 0),
            "doing": by_state.get("doing", 0),
            "blocked": by_state.get("blocked", 0),
            "progress_pct": round(done / total * 100, 1) if total else 0.0,
            "by_area": by_area,
            "review": data.get("review_summary", {}),
        }


class OrderMetricsService:
    """Consulta métricas de pedidos e receita diretamente no banco de dados."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção de dependência."""
        self.session = session

    async def collect(self) -> dict:
        """Retorna contagem de pedidos por status e receita total de pedidos pagos."""
        from app.orders.models import Order, OrderStatus

        rows = await self.session.execute(
            select(Order.status, func.count().label("qty"))
            .group_by(Order.status)
        )
        by_status: dict[str, int] = {}
        for row in rows:
            by_status[row.status.value] = row.qty

        revenue_result = await self.session.scalar(
            select(func.sum(Order.amount)).where(Order.status == OrderStatus.PAID)
        )
        revenue_total = float(revenue_result or Decimal("0"))
        now = datetime.now(UTC)
        rev_7d = await self._revenue_since(OrderStatus.PAID, now - timedelta(days=7))
        rev_30d = await self._revenue_since(OrderStatus.PAID, now - timedelta(days=30))
        return {
            "by_status": by_status,
            "revenue_total": revenue_total,
            "revenue_last_7_days": rev_7d,
            "revenue_last_30_days": rev_30d,
        }

    async def _revenue_since(self, status: object, since: datetime) -> float:
        """Soma Order.amount para os pedidos com status e created_at >= since."""
        from app.orders.models import Order

        result = await self.session.scalar(
            select(func.sum(Order.amount)).where(
                Order.status == status,
                Order.created_at >= since,
            )
        )
        return float(result or Decimal("0"))


class DownloadMetricsService:
    """Coleta métricas de downloads de e-books."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção de dependência."""
        self.session = session

    async def collect(self) -> dict:
        """Retorna total de grants emitidos e total de downloads consumidos."""
        from app.delivery.models import DownloadGrant

        total_granted = await self.session.scalar(
            select(func.count()).select_from(DownloadGrant)
        )
        total_consumed = await self.session.scalar(
            select(func.sum(DownloadGrant.download_count)).select_from(DownloadGrant)
        )
        return {
            "total_granted": int(total_granted or 0),
            "total_consumed": int(total_consumed or 0),
        }


class NewsletterMetricsService:
    """Coleta métricas de inscrições na newsletter."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção de dependência."""
        self.session = session

    async def collect(self) -> dict:
        """Retorna total de inscritos ativos na newsletter."""
        from app.newsletter.models import NewsletterSubscriber

        total_active = await self.session.scalar(
            select(func.count())
            .select_from(NewsletterSubscriber)
            .where(NewsletterSubscriber.active == True)  # noqa: E712
        )
        return {"total_active": int(total_active or 0)}


@router.get("")
async def get_dashboard(
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    """Retorna dados de evolução do projeto e métricas de pedidos e newsletter.

    Combina dados do backlog.json (progresso das tarefas) com métricas
    ao vivo do banco de dados (pedidos por status, receita total, newsletter).
    """
    backlog_data = DashboardDataService(_BACKLOG_PATH).collect()
    order_metrics = await OrderMetricsService(session).collect()
    newsletter_metrics = await NewsletterMetricsService(session).collect()
    download_metrics = await DownloadMetricsService(session).collect()
    backlog_data["orders"] = order_metrics
    backlog_data["newsletter"] = newsletter_metrics
    backlog_data["downloads"] = download_metrics
    return JSONResponse(backlog_data)
