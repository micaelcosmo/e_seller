"""Testes BEQ-16: exclusão de produto via DELETE /api/v1/admin/products/{slug}."""

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


async def _make_product(db_session, slug: str) -> Product:
    """Cria e persiste um produto rascunho."""
    product = Product(
        title=f"Produto {slug}",
        slug=slug,
        author="Autor Teste",
        price=Decimal("19.90"),
        status=ProductStatus.DRAFT,
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def test_delete_requer_auth(client) -> None:
    """DELETE /admin/products/{slug} sem token retorna 401."""
    resp = await client.delete("/api/v1/admin/products/qualquer-slug")
    assert resp.status_code == 401


async def test_delete_produto_inexistente_retorna_404(client, db_session) -> None:
    """DELETE em slug inexistente retorna 404."""
    token = await _staff_token(client, db_session, "beq16_staff1@x.com")
    resp = await client.delete(
        "/api/v1/admin/products/nao-existe-slug",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_delete_produto_draft_sem_pedidos_ok(client, db_session) -> None:
    """DELETE em produto rascunho sem pedidos retorna 204."""
    await _make_product(db_session, "para-deletar")
    token = await _staff_token(client, db_session, "beq16_staff2@x.com")
    resp = await client.delete(
        "/api/v1/admin/products/para-deletar",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204


async def test_delete_produto_com_pedido_pago_retorna_409(
    client, db_session
) -> None:
    """DELETE em produto com pedido pago retorna 409."""
    product = await _make_product(db_session, "com-pedido-pago")
    order = Order(buyer_email="comprador@x.com", status=OrderStatus.PAID, amount=Decimal("19.90"))  # noqa: E501
    db_session.add(order)
    await db_session.flush()
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        unit_price=Decimal("19.90"),
        quantity=1,
    )
    db_session.add(item)
    await db_session.commit()

    token = await _staff_token(client, db_session, "beq16_staff3@x.com")
    resp = await client.delete(
        "/api/v1/admin/products/com-pedido-pago",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409


async def test_delete_produto_com_pedido_pendente_ok(client, db_session) -> None:
    """DELETE em produto com pedido pendente (não pago) é permitido."""
    product = await _make_product(db_session, "pedido-pendente")
    order = Order(buyer_email="pendente@x.com", status=OrderStatus.PENDING, amount=Decimal("19.90"))  # noqa: E501
    db_session.add(order)
    await db_session.flush()
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        unit_price=Decimal("19.90"),
        quantity=1,
    )
    db_session.add(item)
    await db_session.commit()

    token = await _staff_token(client, db_session, "beq16_staff4@x.com")
    resp = await client.delete(
        "/api/v1/admin/products/pedido-pendente",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
