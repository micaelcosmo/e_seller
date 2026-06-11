"""Testes BEQ-23: GET /api/v1/orders/my?status= filtra pedidos do usuário."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.orders.models import Order, OrderStatus
from app.security.passwords import PasswordHasher


async def _setup_user_with_orders(
    client, db_session, email: str
) -> tuple[User, str]:
    """Cria usuário com pedidos PAID e PENDING; retorna (user, token)."""
    hasher = PasswordHasher(iterations=1000)
    user = User(
        email=email,
        password_hash=hasher.hash("pw"),
        role=UserRole.CUSTOMER,
    )
    db_session.add(user)
    await db_session.flush()
    db_session.add(
        Order(
            buyer_email=email,
            amount=Decimal("10.00"),
            status=OrderStatus.PAID,
            user_id=user.id,
        )
    )
    db_session.add(
        Order(
            buyer_email=email,
            amount=Decimal("5.00"),
            status=OrderStatus.PENDING,
            user_id=user.id,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    token = resp.json()["access_token"]
    return user, token


async def test_filtro_status_paid(client, db_session) -> None:
    """?status=paid retorna apenas pedidos pagos do usuário."""
    _, token = await _setup_user_with_orders(client, db_session, "beq23a@x.com")
    resp = await client.get(
        "/api/v1/orders/my?status=paid",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["status"] == "paid"


async def test_filtro_status_pending(client, db_session) -> None:
    """?status=pending retorna apenas pedidos pendentes."""
    _, token = await _setup_user_with_orders(client, db_session, "beq23b@x.com")
    resp = await client.get(
        "/api/v1/orders/my?status=pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["status"] == "pending"


async def test_filtro_status_invalido_vazio(client, db_session) -> None:
    """?status=invalido retorna lista vazia (status desconhecido)."""
    _, token = await _setup_user_with_orders(client, db_session, "beq23c@x.com")
    resp = await client.get(
        "/api/v1/orders/my?status=invalido",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []
