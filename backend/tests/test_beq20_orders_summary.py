"""Testes BEQ-20: GET /api/v1/admin/reports/orders/summary — contagem por status."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.orders.models import Order, OrderStatus
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token JWT."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_summary_requer_staff(client) -> None:
    """GET /admin/reports/orders/summary sem token retorna 401."""
    resp = await client.get("/api/v1/admin/reports/orders/summary")
    assert resp.status_code == 401


async def test_summary_retorna_todos_status(client, db_session) -> None:
    """Resposta inclui todos os valores de OrderStatus com zero ou mais."""
    token = await _staff_token(client, db_session, "beq20_s1@x.com")
    resp = await client.get(
        "/api/v1/admin/reports/orders/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for status in ("pending", "paid", "failed", "cancelled", "refunded"):
        assert status in data


async def test_summary_conta_pedidos_corretamente(client, db_session) -> None:
    """Contagem reflete os pedidos no banco."""
    for _ in range(3):
        db_session.add(
            Order(buyer_email="s@x.com", amount=Decimal("5.00"), status=OrderStatus.PAID)  # noqa: E501
        )
    db_session.add(
        Order(buyer_email="s@x.com", amount=Decimal("5.00"), status=OrderStatus.PENDING)
    )
    await db_session.commit()
    token = await _staff_token(client, db_session, "beq20_s2@x.com")
    resp = await client.get(
        "/api/v1/admin/reports/orders/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["paid"] >= 3
    assert data["pending"] >= 1
