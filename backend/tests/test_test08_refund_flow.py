"""Testes TEST-08: fluxo completo de reembolso + revogação de grant."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str = "refund_staff@x.com") -> str:
    """Cria staff e retorna o token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def _comprar_produto(client, db_session, staff: str, email: str) -> dict:
    """Cria, publica produto e realiza compra aprovada. Retorna order + product."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER)
    )
    await db_session.commit()

    create_resp = await client.post(
        "/api/v1/admin/products",
        json={"title": "Produto Estorno", "price": "39.90"},
        headers={"Authorization": f"Bearer {staff}"},
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["slug"]

    await client.patch(
        f"/api/v1/admin/products/{slug}/status",
        json={"status": "published"},
        headers={"Authorization": f"Bearer {staff}"},
    )

    login = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    token = login.json()["access_token"]

    order_resp = await client.post(
        "/api/v1/orders",
        json={"product_slug": slug, "buyer_email": email},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert order_resp.status_code == 201
    order = order_resp.json()
    reference = order["reference"]

    wh_resp = await client.post(
        "/api/v1/webhooks/mercadopago",
        json={
            "provider_payment_id": f"fake-ref-{reference}",
            "order_reference": reference,
            "provider_status": "approved",
        },
    )
    assert wh_resp.status_code == 200
    return {"order": order, "token": token, "slug": slug}


async def test_download_antes_do_estorno(client, db_session) -> None:
    """Download disponível antes do estorno (grant ativo)."""
    staff = await _staff_token(client, db_session)
    ctx = await _comprar_produto(client, db_session, staff, "pre_ref@x.com")
    slug = ctx["slug"]
    token = ctx["token"]
    # Link de download deve ser emitido com sucesso.
    link_resp = await client.post(
        f"/api/v1/library/{slug}/download-link",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert link_resp.status_code == 200
    assert "url" in link_resp.json()


async def test_refund_bloqueia_download(client, db_session) -> None:
    """Após estorno, o download é bloqueado (grant expirado)."""
    staff = await _staff_token(client, db_session, "refund_s2@x.com")
    ctx = await _comprar_produto(client, db_session, staff, "post_ref@x.com")
    order = ctx["order"]
    token = ctx["token"]
    slug = ctx["slug"]

    # Obter o ID do pagamento via order_id (usando admin).
    # Endpoint de estorno recebe order_reference.
    refund_resp = await client.post(
        "/api/v1/admin/refunds",
        json={"order_reference": order["reference"], "reason": "Teste de estorno"},
        headers={"Authorization": f"Bearer {staff}"},
    )
    assert refund_resp.status_code in (200, 201), refund_resp.text

    # Agora o download deve ser bloqueado (grant expirado).
    link_resp = await client.post(
        f"/api/v1/library/{slug}/download-link",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert link_resp.status_code in (403, 404, 410), (
        f"Esperado 403, 404 ou 410 após estorno, obteve {link_resp.status_code}"
    )


async def test_refund_remove_da_biblioteca(client, db_session) -> None:
    """Após estorno, o produto some da biblioteca do usuário."""
    staff = await _staff_token(client, db_session, "refund_s3@x.com")
    ctx = await _comprar_produto(client, db_session, staff, "lib_ref@x.com")
    order = ctx["order"]
    token = ctx["token"]
    slug = ctx["slug"]

    await client.post(
        "/api/v1/admin/refunds",
        json={"order_reference": order["reference"], "reason": "Teste"},
        headers={"Authorization": f"Bearer {staff}"},
    )

    lib_resp = await client.get(
        "/api/v1/library", headers={"Authorization": f"Bearer {token}"}
    )
    slugs = [p["slug"] for p in lib_resp.json()]
    assert slug not in slugs, "Produto ainda na biblioteca após estorno."
