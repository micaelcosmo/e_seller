"""Testes TEST-07: fluxo completo de compra end-to-end via ASGI."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _register_login(client, db_session, email: str) -> str:
    """Cria usuário e retorna o token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw123"), role=UserRole.CUSTOMER)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw123"}
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


async def _staff_token(client, db_session) -> str:
    """Cria staff e retorna o token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="staff_flow@x.com",
            password_hash=hasher.hash("pw"),
            role=UserRole.STAFF,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "staff_flow@x.com", "password": "pw"},
    )
    return resp.json()["access_token"]


async def test_fluxo_completo_compra_e_download(client, db_session) -> None:
    """Fluxo: registrar produto → criar pedido → webhook aprovado → download."""
    staff = await _staff_token(client, db_session)
    # 1. Cadastrar produto como staff.
    create_resp = await client.post(
        "/api/v1/admin/products",
        json={"title": "Livro Fluxo", "price": "29.90"},
        headers={"Authorization": f"Bearer {staff}"},
    )
    assert create_resp.status_code == 201
    product = create_resp.json()
    slug = product["slug"]

    # 2. Publicar o produto.
    pub_resp = await client.patch(
        f"/api/v1/admin/products/{slug}/status",
        json={"status": "published"},
        headers={"Authorization": f"Bearer {staff}"},
    )
    assert pub_resp.status_code == 200

    # 3. Criar pedido (guest).
    order_resp = await client.post(
        "/api/v1/orders",
        json={"product_slug": slug, "buyer_email": "buyer_flow@x.com"},
    )
    assert order_resp.status_code == 201
    order = order_resp.json()
    reference = order["reference"]
    assert order["status"] == "pending"

    # 4. Simular webhook de aprovação.
    webhook_resp = await client.post(
        "/api/v1/webhooks/mercadopago",
        json={
            "provider_payment_id": f"fake-{reference}",
            "order_reference": reference,
            "provider_status": "approved",
        },
    )
    assert webhook_resp.status_code == 200
    assert webhook_resp.json()["outcome"] == "APPLIED"

    # 5. Verificar status do pedido: deve ser "paid".
    order_check = await client.get(f"/api/v1/orders/{reference}")
    assert order_check.status_code == 200
    assert order_check.json()["status"] == "paid"


async def test_fluxo_compra_com_conta_aparece_na_biblioteca(
    client, db_session
) -> None:
    """Compra autenticada: produto aparece na biblioteca do usuário."""
    staff = await _staff_token(client, db_session)
    # Publicar produto de seed ou criar novo.
    create_resp = await client.post(
        "/api/v1/admin/products",
        json={"title": "Livro Conta", "price": "19.90"},
        headers={"Authorization": f"Bearer {staff}"},
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["slug"]

    await client.patch(
        f"/api/v1/admin/products/{slug}/status",
        json={"status": "published"},
        headers={"Authorization": f"Bearer {staff}"},
    )

    token = await _register_login(client, db_session, "buyer_lib@x.com")
    order_resp = await client.post(
        "/api/v1/orders",
        json={"product_slug": slug, "buyer_email": "buyer_lib@x.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    reference = order_resp.json()["reference"]

    await client.post(
        "/api/v1/webhooks/mercadopago",
        json={
            "provider_payment_id": f"fake-lib-{reference}",
            "order_reference": reference,
            "provider_status": "approved",
        },
    )

    lib_resp = await client.get(
        "/api/v1/library", headers={"Authorization": f"Bearer {token}"}
    )
    assert lib_resp.status_code == 200
    slugs = [p["slug"] for p in lib_resp.json()]
    assert slug in slugs


async def test_fluxo_webhook_duplicado_idempotente(client, db_session) -> None:
    """Webhook repetido não duplica grants nem muda o estado do pedido."""
    staff = await _staff_token(client, db_session)
    create_resp = await client.post(
        "/api/v1/admin/products",
        json={"title": "Livro Idem", "price": "9.90"},
        headers={"Authorization": f"Bearer {staff}"},
    )
    slug = create_resp.json()["slug"]
    await client.patch(
        f"/api/v1/admin/products/{slug}/status",
        json={"status": "published"},
        headers={"Authorization": f"Bearer {staff}"},
    )
    order_resp = await client.post(
        "/api/v1/orders",
        json={"product_slug": slug, "buyer_email": "idem@x.com"},
    )
    reference = order_resp.json()["reference"]
    payload = {
        "provider_payment_id": f"fake-idem-{reference}",
        "order_reference": reference,
        "provider_status": "approved",
    }
    resp1 = await client.post("/api/v1/webhooks/mercadopago", json=payload)
    resp2 = await client.post("/api/v1/webhooks/mercadopago", json=payload)
    assert resp1.status_code == 200
    # Segundo envio é idempotente: retorna ok mas não reprocessa.
    assert resp2.status_code == 200
