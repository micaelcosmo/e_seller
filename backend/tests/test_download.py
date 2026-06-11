"""Testes de download protegido (válido, expirado, limite, token inválido) — async."""

from datetime import datetime

from sqlalchemy import select

from app.delivery.models import DownloadGrant, DownloadLog


async def _aprovar_e_obter_token(client, db_session) -> str:
    """Cria pedido, aprova o pagamento e retorna o token do download_grant."""
    payload = {"product_slug": "python-na-pratica", "buyer_email": "leitor@exemplo.com"}
    reference = (await client.post("/api/v1/orders", json=payload)).json()["reference"]
    webhook = {
        "provider_payment_id": f"mp-{reference}",
        "order_reference": reference,
        "provider_status": "approved",
    }
    await client.post("/api/v1/webhooks/mercadopago", json=webhook)
    result = await db_session.scalars(select(DownloadGrant))
    grant = result.first()
    return grant.token


async def test_download_valido_retorna_arquivo(client, db_session):
    """Com token válido, o download retorna o conteúdo do arquivo."""
    token = await _aprovar_e_obter_token(client, db_session)
    response = await client.get(f"/api/v1/download/{token}")
    assert response.status_code == 200
    assert b"e-book de demonstracao" in response.content


async def test_download_token_invalido_retorna_404(client):
    """Token inexistente retorna 404."""
    response = await client.get("/api/v1/download/token-que-nao-existe")
    assert response.status_code == 404


async def test_download_registra_auditoria(client, db_session):
    """Um download bem-sucedido cria um registro de auditoria (download_log)."""
    token = await _aprovar_e_obter_token(client, db_session)
    await client.get(f"/api/v1/download/{token}")
    result = await db_session.scalars(select(DownloadLog))
    assert len(result.all()) == 1


async def test_download_expirado_retorna_410(client, db_session):
    """Link expirado retorna 410."""
    token = await _aprovar_e_obter_token(client, db_session)
    result = await db_session.scalars(select(DownloadGrant))
    grant = result.first()
    grant.expires_at = datetime(2000, 1, 1, 0, 0, 0)
    await db_session.commit()
    response = await client.get(f"/api/v1/download/{token}")
    assert response.status_code == 410


async def test_download_limite_atingido_retorna_403(client, db_session):
    """Atingido o limite de downloads, retorna 403."""
    token = await _aprovar_e_obter_token(client, db_session)
    result = await db_session.scalars(select(DownloadGrant))
    grant = result.first()
    grant.download_count = grant.max_downloads
    await db_session.commit()
    response = await client.get(f"/api/v1/download/{token}")
    assert response.status_code == 429  # 429 Too Many Requests (limite de downloads)
