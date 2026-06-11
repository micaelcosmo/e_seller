"""Testes da newsletter: inscrição idempotente, cancelamento e validação."""

from sqlalchemy import select

from app.newsletter.models import NewsletterSubscriber


async def test_inscricao_idempotente(client, db_session):
    """Inscrever duas vezes o mesmo e-mail mantém um único registro ativo."""
    await client.post("/api/v1/newsletter/subscribe", json={"email": "n@x.com"})
    resp = await client.post(
        "/api/v1/newsletter/subscribe", json={"email": "n@x.com"}
    )
    assert resp.status_code == 202
    result = await db_session.scalars(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == "n@x.com")
    )
    inscritos = result.all()
    assert len(inscritos) == 1
    assert inscritos[0].active is True


async def test_cancelar_inscricao(client, db_session):
    """Cancelar marca o inscrito como inativo."""
    await client.post("/api/v1/newsletter/subscribe", json={"email": "bye@x.com"})
    resp = await client.post(
        "/api/v1/newsletter/unsubscribe", json={"email": "bye@x.com"}
    )
    assert resp.status_code == 202
    result = await db_session.scalars(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == "bye@x.com")
    )
    assert result.first().active is False


async def test_email_invalido_retorna_422(client):
    """E-mail inválido é rejeitado (422)."""
    resp = await client.post(
        "/api/v1/newsletter/subscribe", json={"email": "invalido"}
    )
    assert resp.status_code == 422
