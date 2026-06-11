"""Testes BEQ-17: GET /api/v1/orders — listagem de pedidos (staff/admin)."""

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


async def test_list_orders_requer_staff(client) -> None:
    """GET /orders sem token retorna 401."""
    resp = await client.get("/api/v1/orders")
    assert resp.status_code == 401


async def test_list_orders_retorna_lista(client, db_session) -> None:
    """Staff recebe lista de pedidos (pode ser vazia)."""
    token = await _staff_token(client, db_session, "beq17_staff@x.com")
    resp = await client.get(
        "/api/v1/orders", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_list_orders_filtro_status(client, db_session) -> None:
    """Filtro por status retorna apenas pedidos com aquele status."""
    order = Order(buyer_email="f@x.com", amount=Decimal("10.00"), status=OrderStatus.PAID)  # noqa: E501
    db_session.add(order)
    await db_session.commit()
    token = await _staff_token(client, db_session, "beq17_staff2@x.com")
    resp = await client.get(
        "/api/v1/orders?status=paid",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert all(i["status"] == "paid" for i in items)


async def test_list_orders_paginacao(client, db_session) -> None:
    """Paginação limita o número de pedidos retornados."""
    for i in range(5):
        db_session.add(
            Order(buyer_email=f"pg{i}@x.com", amount=Decimal("5.00"), status=OrderStatus.PENDING)  # noqa: E501
        )
    await db_session.commit()
    token = await _staff_token(client, db_session, "beq17_staff3@x.com")
    resp = await client.get(
        "/api/v1/orders?page_size=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) <= 2
