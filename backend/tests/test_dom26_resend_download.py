"""Testes DOM-26: POST /api/v1/admin/orders/{ref}/resend-download."""

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


async def _make_paid_order(db_session) -> Order:
    """Cria produto, pedido pago e item."""
    product = Product(
        title="Livro Dom26",
        slug="livro-dom26",
        author="Autor",
        price=Decimal("19.90"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.flush()
    order = Order(buyer_email="buyer@x.com", amount=Decimal("19.90"), status=OrderStatus.PAID)  # noqa: E501
    db_session.add(order)
    await db_session.flush()
    db_session.add(OrderItem(order_id=order.id, product_id=product.id, unit_price=Decimal("19.90"), quantity=1))  # noqa: E501
    await db_session.commit()
    return order


async def test_resend_requer_staff(client) -> None:
    """POST sem token retorna 401."""
    resp = await client.post("/api/v1/admin/orders/QUALQUER/resend-download")
    assert resp.status_code == 401


async def test_resend_pedido_inexistente_404(client, db_session) -> None:
    """Referência inexistente retorna 404."""
    token = await _staff_token(client, db_session, "dom26_s1@x.com")
    resp = await client.post(
        "/api/v1/admin/orders/NAO-EXISTE/resend-download",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_resend_pedido_nao_pago_422(client, db_session) -> None:
    """Pedido pendente retorna 422."""
    order = Order(buyer_email="p@x.com", amount=Decimal("5.00"), status=OrderStatus.PENDING)  # noqa: E501
    db_session.add(order)
    await db_session.commit()
    token = await _staff_token(client, db_session, "dom26_s2@x.com")
    resp = await client.post(
        f"/api/v1/admin/orders/{order.reference}/resend-download",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


async def test_resend_pedido_pago_retorna_url(client, db_session) -> None:
    """Pedido pago com item retorna download_url."""
    order = await _make_paid_order(db_session)
    token = await _staff_token(client, db_session, "dom26_s3@x.com")
    resp = await client.post(
        f"/api/v1/admin/orders/{order.reference}/resend-download",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "download_url" in data
    assert "/api/v1/download/" in data["download_url"]
