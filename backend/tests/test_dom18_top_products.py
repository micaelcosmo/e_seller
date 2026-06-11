"""Testes DOM-18: ranking de produtos mais vendidos."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_top_products_requer_auth(client) -> None:
    """GET /admin/reports/top-products sem token retorna 401."""
    resp = await client.get("/api/v1/admin/reports/top-products")
    assert resp.status_code == 401


async def test_top_products_retorna_lista(client, db_session) -> None:
    """Staff obtém lista de top produtos (pode ser vazia se não houver vendas)."""
    token = await _staff_token(client, db_session, "dom18_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/reports/top-products",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_top_products_apos_venda(client, db_session) -> None:
    """Após uma venda, o produto aparece no ranking."""
    token = await _staff_token(client, db_session, "dom18_staff2@x.com")
    # Cria pedido e aprova o pagamento.
    payload = {"product_slug": "python-na-pratica", "buyer_email": "comprador@x.com"}
    reference = (await client.post("/api/v1/orders", json=payload)).json()["reference"]
    webhook_payload = {
        "provider_payment_id": f"mp-dom18-{reference}",
        "order_reference": reference,
        "provider_status": "approved",
    }
    await client.post("/api/v1/webhooks/mercadopago", json=webhook_payload)
    resp = await client.get(
        "/api/v1/admin/reports/top-products",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    slugs_or_ids = [item["product_id"] for item in items]
    assert any(i is not None for i in slugs_or_ids)
    for item in items:
        assert "title" in item
        assert "units_sold" in item
        assert item["units_sold"] >= 1
