"""Testes BEQ-25: paginação do painel admin de pedidos com X-Total-Count."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.core.config import get_settings
from app.orders.models import Order, OrderStatus
from app.security.jwt import JwtService
from app.security.passwords import PasswordHasher


async def _admin_token(db_session) -> str:
    """Cria usuário admin e retorna seu token JWT."""
    settings = get_settings()
    hasher = PasswordHasher(settings.password_hash_iterations)
    user = User(
        email="admin_beq25@test.com",
        password_hash=hasher.hash("admin"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    jwt = JwtService(secret_key=settings.app_secret_key)
    return jwt.issue(user.email)


async def _create_order(db_session, email: str, status: OrderStatus) -> Order:
    """Cria e persiste um pedido de teste."""
    order = Order(
        buyer_email=email,
        amount=Decimal("29.90"),
        status=status,
    )
    db_session.add(order)
    await db_session.commit()
    return order


async def test_list_admin_orders_retorna_x_total_count(client, db_session) -> None:
    """GET /orders (admin) retorna header X-Total-Count com total de pedidos."""
    token = await _admin_token(db_session)
    for i in range(3):
        await _create_order(db_session, f"buyer{i}@test.com", OrderStatus.PENDING)
    resp = await client.get(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "x-total-count" in resp.headers
    assert int(resp.headers["x-total-count"]) >= 3


async def test_paginacao_page_size_limita_resultados(client, db_session) -> None:
    """GET /orders?page_size=2 retorna no máximo 2 pedidos."""
    token = await _admin_token(db_session)
    for i in range(5):
        await _create_order(db_session, f"pager{i}@test.com", OrderStatus.PENDING)
    resp = await client.get(
        "/api/v1/orders?page_size=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) <= 2


async def test_x_total_count_respeita_filtro_status(client, db_session) -> None:
    """X-Total-Count reflete apenas pedidos do status filtrado."""
    token = await _admin_token(db_session)
    await _create_order(db_session, "paid@test.com", OrderStatus.PAID)
    await _create_order(db_session, "pending@test.com", OrderStatus.PENDING)
    resp = await client.get(
        "/api/v1/orders?status=paid",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    total = int(resp.headers["x-total-count"])
    items = resp.json()
    assert total == len(items)
    assert all(o["status"] == "paid" for o in items)
