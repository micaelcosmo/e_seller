"""Testes ADM-09: painel admin de inscritos na newsletter."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.core.config import get_settings
from app.newsletter.models import NewsletterSubscriber
from app.security.jwt import JwtService
from app.security.passwords import PasswordHasher


async def _admin_token(db_session) -> str:
    """Cria usuário admin e retorna seu JWT."""
    settings = get_settings()
    hasher = PasswordHasher(settings.password_hash_iterations)
    user = User(
        email="admin_adm09@test.com",
        password_hash=hasher.hash("x"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return JwtService(secret_key=settings.app_secret_key).issue(user.email)


async def test_lista_inscritos_retorna_x_total_count(client, db_session) -> None:
    """GET /admin/newsletter/subscribers retorna header X-Total-Count."""
    token = await _admin_token(db_session)
    for i in range(3):
        db_session.add(NewsletterSubscriber(email=f"sub{i}@test.com", active=True))
    await db_session.commit()
    resp = await client.get(
        "/api/v1/admin/newsletter/subscribers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "x-total-count" in resp.headers
    assert int(resp.headers["x-total-count"]) >= 3


async def test_filtro_active_true_retorna_apenas_ativos(client, db_session) -> None:
    """Filtro ?active=true retorna apenas inscritos ativos."""
    token = await _admin_token(db_session)
    db_session.add(NewsletterSubscriber(email="ativo@test.com", active=True))
    db_session.add(NewsletterSubscriber(email="inativo@test.com", active=False))
    await db_session.commit()
    resp = await client.get(
        "/api/v1/admin/newsletter/subscribers?active=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert all(item["active"] for item in items)


async def test_sem_autenticacao_retorna_401(client) -> None:
    """Endpoint admin requer autenticação (401 sem token)."""
    resp = await client.get("/api/v1/admin/newsletter/subscribers")
    assert resp.status_code == 401
