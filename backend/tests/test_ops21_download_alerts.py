"""Testes OPS-21: alertas de estoque de downloads (remaining_downloads <= 1)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.accounts.models import User, UserRole
from app.catalog.models import Product, ProductStatus
from app.delivery.models import DownloadGrant
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


async def _make_grant(
    db_session,
    max_downloads: int,
    download_count: int,
) -> DownloadGrant:
    """Cria um DownloadGrant com valores definidos."""
    product = Product(
        title="Livro Alerta",
        slug=f"livro-alerta-{max_downloads}-{download_count}",
        price=Decimal("10.00"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.flush()

    order = Order(
        buyer_email="test@ops21.com",
        amount=Decimal("10.00"),
        status=OrderStatus.PAID,
    )
    db_session.add(order)
    await db_session.flush()

    item = OrderItem(
        order_id=order.id, product_id=product.id, unit_price=Decimal("10.00")
    )
    db_session.add(item)
    await db_session.flush()

    grant = DownloadGrant(
        order_item_id=item.id,
        product_id=product.id,
        token=f"tok-ops21-{max_downloads}-{download_count}",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        max_downloads=max_downloads,
        download_count=download_count,
    )
    db_session.add(grant)
    await db_session.commit()
    return grant


async def test_sem_grants_baixos_nao_emite_alerta(client, db_session) -> None:
    """Sem grants com estoque baixo, não deve haver alerta de downloads."""
    await _make_grant(db_session, max_downloads=5, download_count=2)
    token = await _staff_token(client, db_session, "ops21_a@x.com")
    resp = await client.get(
        "/api/v1/admin/alerts/check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    nomes = [a["name"] for a in resp.json().get("alerts", [])]
    assert "estoque_downloads_baixo" not in nomes


async def test_grant_com_zero_restantes_emite_alerta(client, db_session) -> None:
    """Grant com download_count == max_downloads emite alerta de estoque baixo."""
    await _make_grant(db_session, max_downloads=3, download_count=3)
    token = await _staff_token(client, db_session, "ops21_b@x.com")
    resp = await client.get(
        "/api/v1/admin/alerts/check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    nomes = [a["name"] for a in resp.json().get("alerts", [])]
    assert "estoque_downloads_baixo" in nomes


async def test_grant_com_um_restante_emite_alerta(client, db_session) -> None:
    """Grant com exatamente 1 download restante emite alerta de estoque baixo."""
    await _make_grant(db_session, max_downloads=5, download_count=4)
    token = await _staff_token(client, db_session, "ops21_c@x.com")
    resp = await client.get(
        "/api/v1/admin/alerts/check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    nomes = [a["name"] for a in resp.json().get("alerts", [])]
    assert "estoque_downloads_baixo" in nomes
