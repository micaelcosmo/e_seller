"""Testes OPS-15: GET /api/v1/dashboard inclui orders.by_status e revenue.total."""

from __future__ import annotations

from decimal import Decimal

from app.orders.models import Order, OrderStatus


async def test_dashboard_sem_pedidos(client, db_session) -> None:
    """Dashboard sem pedidos retorna by_status vazio e revenue_total 0."""
    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "orders" in data
    orders = data["orders"]
    assert "by_status" in orders
    assert "revenue_total" in orders
    assert "revenue_last_7_days" in orders
    assert "revenue_last_30_days" in orders
    assert orders["revenue_total"] == 0.0
    assert orders["revenue_last_7_days"] == 0.0
    assert orders["revenue_last_30_days"] == 0.0


async def test_dashboard_com_pedidos_pagos(client, db_session) -> None:
    """Dashboard reflete pedidos pagos na receita total."""
    db_session.add(
        Order(
            buyer_email="a@x.com",
            amount=Decimal("50.00"),
            status=OrderStatus.PAID,
        )
    )
    db_session.add(
        Order(
            buyer_email="b@x.com",
            amount=Decimal("30.00"),
            status=OrderStatus.PAID,
        )
    )
    db_session.add(
        Order(
            buyer_email="c@x.com",
            amount=Decimal("20.00"),
            status=OrderStatus.PENDING,
        )
    )
    await db_session.commit()
    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    orders = resp.json()["orders"]
    assert orders["by_status"].get("paid") == 2
    assert orders["by_status"].get("pending") == 1
    assert orders["revenue_total"] == 80.0
