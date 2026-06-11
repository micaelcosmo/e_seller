"""Testes ADM-13: listagem admin de DownloadGrants."""

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
    slug_tag: str,
    download_count: int = 1,
    expired: bool = False,
) -> DownloadGrant:
    """Cria DownloadGrant com dados mínimos no banco."""
    product = Product(
        title=f"Livro ADM13 {slug_tag}",
        slug=f"adm13-{slug_tag}",
        price=Decimal("10.00"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.flush()
    order = Order(
        buyer_email=f"{slug_tag}@adm13.com",
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
    if expired:
        expires = datetime.now(UTC) - timedelta(days=1)
    else:
        expires = datetime.now(UTC) + timedelta(days=7)
    grant = DownloadGrant(
        order_item_id=item.id,
        product_id=product.id,
        token=f"tok-adm13-{slug_tag}",
        expires_at=expires,
        max_downloads=3,
        download_count=download_count,
    )
    db_session.add(grant)
    return grant


async def test_lista_grants_retorna_x_total_count(client, db_session) -> None:
    """GET /admin/downloads deve retornar header X-Total-Count."""
    await _make_grant(db_session, "a")
    await db_session.commit()
    token = await _staff_token(client, db_session, "adm13_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/downloads",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "x-total-count" in resp.headers
    assert int(resp.headers["x-total-count"]) >= 1


async def test_filtra_por_product_id(client, db_session) -> None:
    """?product_id= deve retornar apenas grants do produto indicado."""
    g1 = await _make_grant(db_session, "b")
    await _make_grant(db_session, "c")
    await db_session.flush()
    product_id = g1.product_id
    await db_session.commit()

    token = await _staff_token(client, db_session, "adm13b_staff@x.com")
    resp = await client.get(
        f"/api/v1/admin/downloads?product_id={product_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    for item in items:
        assert item["product_id"] == product_id


async def test_filtra_expirados(client, db_session) -> None:
    """?expired=true deve retornar apenas grants com expires_at no passado."""
    await _make_grant(db_session, "d", expired=True)
    await _make_grant(db_session, "e", expired=False)
    await db_session.commit()

    token = await _staff_token(client, db_session, "adm13c_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/downloads?expired=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert int(resp.headers["x-total-count"]) >= 1
    items = resp.json()
    for item in items:
        expires = datetime.fromisoformat(item["expires_at"])
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        assert expires < datetime.now(UTC)
