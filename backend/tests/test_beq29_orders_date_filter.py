"""Testes BEQ-29: filtro de data em listagem de pedidos admin."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.core.config import get_settings
from app.orders.models import Order, OrderStatus
from app.security.jwt import JwtService
from app.security.passwords import PasswordHasher


async def _admin_token(db_session) -> str:
    """Cria usuário admin e retorna seu JWT."""
    settings = get_settings()
    hasher = PasswordHasher(settings.password_hash_iterations)
    user = User(
        email="admin_beq29@test.com",
        password_hash=hasher.hash("x"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return JwtService(secret_key=settings.app_secret_key).issue(user.email)


async def _create_order(db_session, email: str) -> Order:
    """Cria pedido de teste."""
    order = Order(
        buyer_email=email,
        amount=Decimal("9.90"),
        status=OrderStatus.PENDING,
    )
    db_session.add(order)
    await db_session.commit()
    return order


async def test_sem_filtro_data_retorna_todos(client, db_session) -> None:
    """GET /orders sem filtro de data retorna todos os pedidos."""
    token = await _admin_token(db_session)
    await _create_order(db_session, "a@test.com")
    resp = await client.get(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert int(resp.headers["x-total-count"]) >= 1


async def test_date_from_futuro_retorna_zero(client, db_session) -> None:
    """Filtro ?date_from= no futuro retorna lista vazia."""
    token = await _admin_token(db_session)
    await _create_order(db_session, "b@test.com")
    resp = await client.get(
        "/api/v1/orders?date_from=2099-01-01",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert int(resp.headers["x-total-count"]) == 0
    assert resp.json() == []


async def test_date_invalido_retorna_lista_vazia(client, db_session) -> None:
    """Filtro com data inválida retorna lista vazia (não 422)."""
    token = await _admin_token(db_session)
    resp = await client.get(
        "/api/v1/orders?date_from=nao-e-data",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []
