"""Testes BEQ-18: GET /api/v1/orders/admin/{reference} — detalhe de pedido (admin)."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.catalog.models import Product, ProductStatus
from app.orders.models import Order, OrderItem, OrderStatus
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


async def test_detail_requer_staff(client) -> None:
    """GET /orders/admin/{ref} sem token retorna 401."""
    resp = await client.get("/api/v1/orders/admin/QUALQUER-REF")
    assert resp.status_code == 401


async def test_detail_nao_encontrado_retorna_404(client, db_session) -> None:
    """GET /orders/admin/{ref} com referência inexistente retorna 404."""
    token = await _staff_token(client, db_session, "beq18_s1@x.com")
    resp = await client.get(
        "/api/v1/orders/admin/REF-INVALIDA",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_detail_retorna_pedido_com_campos(client, db_session) -> None:
    """GET /orders/admin/{ref} retorna referência, status, amount, buyer_email, items."""  # noqa: E501
    product = Product(
        title="Livro Test",
        slug="livro-test-beq18",
        author="Autor",
        price=Decimal("25.00"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.flush()
    order = Order(
        buyer_email="comprador@x.com",
        amount=Decimal("25.00"),
        status=OrderStatus.PAID,
    )
    db_session.add(order)
    await db_session.flush()
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        unit_price=Decimal("25.00"),
        quantity=1,
    )
    db_session.add(item)
    await db_session.commit()

    token = await _staff_token(client, db_session, "beq18_s2@x.com")
    resp = await client.get(
        f"/api/v1/orders/admin/{order.reference}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["reference"] == order.reference
    assert data["buyer_email"] == "comprador@x.com"
    assert data["status"] == "paid"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product.id
