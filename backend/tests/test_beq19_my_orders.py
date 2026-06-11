"""Testes BEQ-19: GET /api/v1/orders/my — pedidos do usuário autenticado."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.orders.models import Order, OrderStatus
from app.security.passwords import PasswordHasher


async def _user_token(client, db_session, email: str) -> str:
    """Cria conta cliente e retorna token JWT."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def _make_order(db_session, user_id: int, status: OrderStatus) -> Order:
    """Cria e persiste um pedido para um usuário."""
    order = Order(
        buyer_email="test@x.com",
        user_id=user_id,
        amount=Decimal("29.90"),
        status=status,
    )
    db_session.add(order)
    await db_session.commit()
    return order


async def test_my_orders_requer_auth(client) -> None:
    """GET /orders/my sem token retorna 401."""
    resp = await client.get("/api/v1/orders/my")
    assert resp.status_code == 401


async def test_my_orders_lista_vazia(client, db_session) -> None:
    """Usuário sem pedidos recebe lista vazia."""
    token = await _user_token(client, db_session, "beq19_sem@x.com")
    resp = await client.get("/api/v1/orders/my", headers={"Authorization": f"Bearer {token}"})  # noqa: E501
    assert resp.status_code == 200
    assert resp.json() == []


async def test_my_orders_retorna_pedidos_do_usuario(client, db_session) -> None:
    """Pedidos do usuário autenticado são retornados; pedidos de outros não aparecem."""
    hasher = PasswordHasher(iterations=1000)
    user_a = User(email="beq19_a@x.com", password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER)  # noqa: E501
    user_b = User(email="beq19_b@x.com", password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER)  # noqa: E501
    db_session.add_all([user_a, user_b])
    await db_session.flush()
    order_a = Order(buyer_email="beq19_a@x.com", user_id=user_a.id, amount=Decimal("19.90"), status=OrderStatus.PAID)  # noqa: E501
    order_b = Order(buyer_email="beq19_b@x.com", user_id=user_b.id, amount=Decimal("9.90"), status=OrderStatus.PAID)  # noqa: E501
    db_session.add_all([order_a, order_b])
    await db_session.commit()

    resp_login = await client.post(
        "/api/v1/auth/token", data={"username": "beq19_a@x.com", "password": "pw"}
    )
    token = resp_login.json()["access_token"]
    resp = await client.get("/api/v1/orders/my", headers={"Authorization": f"Bearer {token}"})  # noqa: E501
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["reference"] == order_a.reference


async def test_my_orders_paginacao(client, db_session) -> None:
    """Paginação limita o número de pedidos retornados."""
    hasher = PasswordHasher(iterations=1000)
    user = User(email="beq19_pg@x.com", password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER)  # noqa: E501
    db_session.add(user)
    await db_session.flush()
    for _i in range(5):
        db_session.add(
            Order(buyer_email="beq19_pg@x.com", user_id=user.id, amount=Decimal("5.00"), status=OrderStatus.PENDING)  # noqa: E501
        )
    await db_session.commit()

    resp_login = await client.post(
        "/api/v1/auth/token", data={"username": "beq19_pg@x.com", "password": "pw"}
    )
    token = resp_login.json()["access_token"]
    resp = await client.get(
        "/api/v1/orders/my?page_size=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 2
