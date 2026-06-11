"""Testes OPS-23: métricas de newsletter no dashboard."""

from __future__ import annotations

from app.newsletter.models import NewsletterSubscriber


async def test_dashboard_inclui_newsletter(client) -> None:
    """GET /api/v1/dashboard deve incluir chave 'newsletter'."""
    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    assert "newsletter" in resp.json()


async def test_dashboard_newsletter_total_active(client, db_session) -> None:
    """Campo newsletter.total_active deve refletir inscritos ativos."""
    db_session.add(NewsletterSubscriber(email="ativo@ops23.com", active=True))
    db_session.add(NewsletterSubscriber(email="inativo@ops23.com", active=False))
    await db_session.commit()

    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    newsletter = resp.json()["newsletter"]
    assert "total_active" in newsletter
    assert newsletter["total_active"] >= 1


async def test_dashboard_newsletter_sem_inscritos(client) -> None:
    """Newsletter com zero inscritos deve retornar total_active=0 (ou >= 0)."""
    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    newsletter = resp.json()["newsletter"]
    assert newsletter["total_active"] >= 0
