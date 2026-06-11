"""Testes BEQ-22: GET /api/v1/orders?ref={reference} — busca por referência."""

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


async def test_filtro_referencia_exata(client, db_session) -> None:
    """?ref= retorna apenas o pedido com aquela referência."""
    order = Order(buyer_email="a@x.com", amount=Decimal("10.00"), status=OrderStatus.PAID)  # noqa: E501
    db_session.add(order)
    await db_session.commit()
    token = await _staff_token(client, db_session, "beq22_s1@x.com")
    resp = await client.get(
        f"/api/v1/orders?ref={order.reference}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["reference"] == order.reference


async def test_filtro_referencia_inexistente_vazio(client, db_session) -> None:
    """?ref= com referência inexistente retorna lista vazia."""
    token = await _staff_token(client, db_session, "beq22_s2@x.com")
    resp = await client.get(
        "/api/v1/orders?ref=REF-QUE-NAO-EXISTE",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []
