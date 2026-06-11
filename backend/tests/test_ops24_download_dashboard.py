"""Testes OPS-24: métricas de downloads no endpoint /dashboard."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.catalog.models import Product, ProductStatus
from app.delivery.models import DownloadGrant
from app.orders.models import Order, OrderItem, OrderStatus


async def _make_grant(
    db_session,
    email_tag: str,
    max_downloads: int = 3,
    download_count: int = 1,
) -> DownloadGrant:
    """Cria DownloadGrant com OrderItem no banco e retorna o objeto."""
    product = Product(
        title=f"Livro Ops24 {email_tag}",
        slug=f"ops24-{email_tag}",
        price=Decimal("10.00"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.flush()
    order = Order(
        buyer_email=f"{email_tag}@ops24.com",
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
        token=f"tok-ops24-{email_tag}",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        max_downloads=max_downloads,
        download_count=download_count,
    )
    db_session.add(grant)
    return grant


async def test_dashboard_tem_chave_downloads(client, db_session) -> None:
    """GET /api/v1/dashboard deve incluir a chave 'downloads'."""
    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    assert "downloads" in resp.json()


async def test_dashboard_downloads_total_granted(client, db_session) -> None:
    """'downloads.total_granted' deve refletir o número de grants no banco."""
    await _make_grant(db_session, "a", max_downloads=3, download_count=2)
    await _make_grant(db_session, "b", max_downloads=5, download_count=0)
    await db_session.commit()

    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["downloads"]["total_granted"] >= 2


async def test_dashboard_downloads_total_consumed(client, db_session) -> None:
    """'downloads.total_consumed' deve refletir a soma de download_count."""
    await _make_grant(db_session, "c", max_downloads=3, download_count=2)
    await _make_grant(db_session, "d", max_downloads=5, download_count=3)
    await db_session.commit()

    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["downloads"]["total_consumed"] >= 5
