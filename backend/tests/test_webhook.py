"""Testes do webhook (aprovação, idempotência, recusa, segurança) — async."""

from sqlalchemy import select

from app.delivery.models import DownloadGrant


async def _criar_pedido(client) -> str:
    """Cria um pedido e retorna a referência."""
    payload = {"product_slug": "python-na-pratica", "buyer_email": "leitor@exemplo.com"}
    response = await client.post("/api/v1/orders", json=payload)
    return response.json()["reference"]


async def _contar_grants(db_session) -> int:
    """Conta os download_grants existentes."""
    result = await db_session.scalars(select(DownloadGrant))
    return len(result.all())


async def test_webhook_aprovado_marca_pago_e_emite_grant(client, db_session):
    """Webhook aprovado leva o pedido a 'paid' e cria um download_grant."""
    reference = await _criar_pedido(client)
    payload = {
        "provider_payment_id": f"mp-{reference}",
        "order_reference": reference,
        "provider_status": "approved",
    }
    response = await client.post("/api/v1/webhooks/mercadopago", json=payload)
    assert response.status_code == 200
    assert response.json()["outcome"] == "APPLIED"

    status = (await client.get(f"/api/v1/orders/{reference}")).json()["status"]
    assert status == "paid"
    assert await _contar_grants(db_session) == 1


async def test_webhook_duplicado_e_idempotente(client, db_session):
    """Reenviar o mesmo webhook não cria efeitos duplicados."""
    reference = await _criar_pedido(client)
    payload = {
        "provider_payment_id": f"mp-{reference}",
        "order_reference": reference,
        "provider_status": "approved",
    }
    await client.post("/api/v1/webhooks/mercadopago", json=payload)
    second = await client.post("/api/v1/webhooks/mercadopago", json=payload)
    assert second.json()["outcome"] == "ALREADY_PROCESSED"
    assert await _contar_grants(db_session) == 1


async def test_webhook_recusado_marca_falho_sem_grant(client, db_session):
    """Webhook recusado leva o pedido a 'failed' e não emite grant."""
    reference = await _criar_pedido(client)
    payload = {
        "provider_payment_id": f"mp-{reference}",
        "order_reference": reference,
        "provider_status": "rejected",
    }
    await client.post("/api/v1/webhooks/mercadopago", json=payload)
    status = (await client.get(f"/api/v1/orders/{reference}")).json()["status"]
    assert status == "failed"
    assert await _contar_grants(db_session) == 0


async def test_retorno_sem_webhook_nao_libera(client, db_session):
    """Sem webhook confirmado, o pedido segue pendente e sem download."""
    reference = await _criar_pedido(client)
    status = (await client.get(f"/api/v1/orders/{reference}")).json()["status"]
    assert status == "pending"
    assert await _contar_grants(db_session) == 0
