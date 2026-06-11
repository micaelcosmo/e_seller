"""Testes de estorno (refund): autorização, revogação de posse e estados."""

from sqlalchemy import select

from app.accounts.models import User, UserRole
from app.delivery.models import DownloadGrant
from app.orders.models import Order, OrderItem
from app.security.passwords import PasswordHasher


async def _registrar_logar(client, email: str) -> dict:
    """Registra e loga um comprador; retorna o header de autorização."""
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "123456"}
    )
    login = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "123456"}
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def _admin_headers(client, db_session) -> dict:
    """Cria um admin no banco de teste e devolve o header de autorização."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="chefe@x.com",
            password_hash=hasher.hash("123456"),
            role=UserRole.ADMIN,
        )
    )
    await db_session.commit()
    login = await client.post(
        "/api/v1/auth/token", data={"username": "chefe@x.com", "password": "123456"}
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def _comprar_pagar(client, headers: dict, slug: str) -> str:
    """Compra logado, aprova o pagamento e retorna a referência do pedido."""
    order = (
        await client.post(
            "/api/v1/orders",
            json={"product_slug": slug, "buyer_email": "x@x.com"},
            headers=headers,
        )
    ).json()
    reference = order["reference"]
    await client.post(
        "/api/v1/webhooks/mercadopago",
        json={
            "provider_payment_id": f"pay-{reference}",
            "order_reference": reference,
            "provider_status": "approved",
        },
    )
    return reference


async def test_estorno_revoga_posse(client, db_session):
    """Estornar um pedido pago marca REFUNDED e remove o e-book da biblioteca."""
    comprador = await _registrar_logar(client, "buyer@x.com")
    reference = await _comprar_pagar(client, comprador, "python-na-pratica")
    biblioteca = await client.get("/api/v1/library", headers=comprador)
    assert len(biblioteca.json()) == 1

    admin = await _admin_headers(client, db_session)
    resp = await client.post(
        "/api/v1/admin/refunds",
        headers=admin,
        json={"order_reference": reference, "reason": "Pedido do cliente"},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "completed"

    biblioteca_depois = await client.get("/api/v1/library", headers=comprador)
    assert len(biblioteca_depois.json()) == 0


async def _grant_token_do_pedido(db_session, reference: str) -> str:
    """Recupera o token do DownloadGrant emitido para o pedido."""
    order = (
        await db_session.scalars(
            select(Order).where(Order.reference == reference)
        )
    ).first()
    item = (
        await db_session.scalars(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
    ).first()
    grant = (
        await db_session.scalars(
            select(DownloadGrant).where(DownloadGrant.order_item_id == item.id)
        )
    ).first()
    return grant.token


async def test_estorno_invalida_link_de_download(client, db_session):
    """Após o estorno, o link de download emitido deixa de funcionar (410)."""
    comprador = await _registrar_logar(client, "buyer-dl@x.com")
    reference = await _comprar_pagar(client, comprador, "python-na-pratica")
    token = await _grant_token_do_pedido(db_session, reference)

    antes = await client.get(f"/api/v1/download/{token}")
    assert antes.status_code == 200

    admin = await _admin_headers(client, db_session)
    estorno = await client.post(
        "/api/v1/admin/refunds",
        headers=admin,
        json={"order_reference": reference},
    )
    assert estorno.status_code == 201

    depois = await client.get(f"/api/v1/download/{token}")
    assert depois.status_code == 410


async def test_estorno_exige_admin(client):
    """Comprador comum não pode estornar (403)."""
    comprador = await _registrar_logar(client, "buyer2@x.com")
    reference = await _comprar_pagar(client, comprador, "fastapi-do-zero")
    resp = await client.post(
        "/api/v1/admin/refunds",
        headers=comprador,
        json={"order_reference": reference},
    )
    assert resp.status_code == 403


async def test_estorno_de_pedido_nao_pago_falha(client, db_session):
    """Estornar um pedido sem pagamento aprovado retorna 409."""
    comprador = await _registrar_logar(client, "buyer3@x.com")
    order = (
        await client.post(
            "/api/v1/orders",
            json={"product_slug": "arquitetura-limpa-web", "buyer_email": "x@x.com"},
            headers=comprador,
        )
    ).json()
    admin = await _admin_headers(client, db_session)
    resp = await client.post(
        "/api/v1/admin/refunds",
        headers=admin,
        json={"order_reference": order["reference"]},
    )
    assert resp.status_code == 409


async def test_valor_de_estorno_acima_do_total_falha(client, db_session):
    """Estorno com valor maior que o total do pedido é rejeitado (422)."""
    comprador = await _registrar_logar(client, "buyer4@x.com")
    reference = await _comprar_pagar(client, comprador, "python-na-pratica")
    admin = await _admin_headers(client, db_session)
    resp = await client.post(
        "/api/v1/admin/refunds",
        headers=admin,
        json={"order_reference": reference, "amount": "9999.00"},
    )
    assert resp.status_code == 422
