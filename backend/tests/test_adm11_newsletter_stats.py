"""Testes ADM-11: endpoint de estatísticas da newsletter."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.newsletter.models import NewsletterSubscriber
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


async def test_stats_retorna_campos_esperados(client, db_session) -> None:
    """GET /admin/newsletter/stats deve retornar os campos de estatísticas."""
    token = await _staff_token(client, db_session, "adm11_a@x.com")
    resp = await client.get(
        "/api/v1/admin/newsletter/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_subscribers" in data
    assert "active" in data
    assert "inactive" in data
    assert "new_last_30_days" in data


async def test_stats_contagem_correta(client, db_session) -> None:
    """Stats deve refletir o número correto de inscritos ativos e inativos."""
    db_session.add(NewsletterSubscriber(email="ativo1@adm11.com", active=True))
    db_session.add(NewsletterSubscriber(email="ativo2@adm11.com", active=True))
    db_session.add(NewsletterSubscriber(email="inativo@adm11.com", active=False))
    await db_session.commit()

    token = await _staff_token(client, db_session, "adm11_b@x.com")
    resp = await client.get(
        "/api/v1/admin/newsletter/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["active"] >= 2
    assert data["inactive"] >= 1
    assert data["total_subscribers"] >= 3


async def test_stats_requer_autenticacao(client) -> None:
    """GET /admin/newsletter/stats sem token deve retornar 401."""
    resp = await client.get("/api/v1/admin/newsletter/stats")
    assert resp.status_code == 401
