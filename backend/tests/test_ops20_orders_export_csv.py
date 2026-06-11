"""Testes OPS-20: export CSV de pedidos para administradores."""

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
        email="admin_ops20@test.com",
        password_hash=hasher.hash("x"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return JwtService(secret_key=settings.app_secret_key).issue(user.email)


async def test_export_csv_retorna_content_type_csv(client, db_session) -> None:
    """GET /orders/export retorna Content-Type text/csv."""
    token = await _admin_token(db_session)
    resp = await client.get(
        "/api/v1/orders/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


async def test_export_csv_tem_cabecalho(client, db_session) -> None:
    """GET /orders/export retorna CSV com linha de cabeçalho correta."""
    token = await _admin_token(db_session)
    resp = await client.get(
        "/api/v1/orders/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    first_line = resp.text.split("\n")[0]
    assert "reference" in first_line
    assert "buyer_email" in first_line
    assert "status" in first_line


async def test_export_csv_inclui_pedidos(client, db_session) -> None:
    """GET /orders/export inclui pedidos criados no CSV."""
    token = await _admin_token(db_session)
    order = Order(
        buyer_email="csv@test.com",
        amount=Decimal("49.90"),
        status=OrderStatus.PAID,
    )
    db_session.add(order)
    await db_session.commit()
    resp = await client.get(
        "/api/v1/orders/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "csv@test.com" in resp.text
