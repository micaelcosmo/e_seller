"""Testes SEC-16: bloqueio por força bruta no login (5 falhas em 5 min)."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.core.rate_limit import LoginFailTracker
from app.security.passwords import PasswordHasher


async def _create_user(db_session, email: str, password: str) -> None:
    """Cria um usuário ativo para testes de login."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash(password), role=UserRole.CUSTOMER)
    )
    await db_session.commit()


async def test_login_bem_sucedido_nao_e_bloqueado(client, db_session) -> None:
    """Login com credenciais corretas retorna 200 mesmo após tentativas falhas isoladas."""  # noqa: E501
    await _create_user(db_session, "sec16_ok@x.com", "senha123")
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "sec16_ok@x.com", "password": "senha123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_bloqueio_apos_cinco_falhas(client, db_session) -> None:
    """Após 5 tentativas falhas com mesmo e-mail, login retorna 429."""
    await _create_user(db_session, "sec16_block@x.com", "correta")
    for _ in range(5):
        await client.post(
            "/api/v1/auth/token",
            data={"username": "sec16_block@x.com", "password": "errada"},
        )
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "sec16_block@x.com", "password": "correta"},
    )
    assert resp.status_code == 429


async def test_login_fail_tracker_isolado() -> None:
    """LoginFailTracker bloqueia após atingir o limite de falhas."""
    tracker = LoginFailTracker(max_failures=3, window_seconds=60)
    assert not tracker.is_blocked("user@x.com")
    tracker.record_failure("user@x.com")
    tracker.record_failure("user@x.com")
    assert not tracker.is_blocked("user@x.com")
    tracker.record_failure("user@x.com")
    assert tracker.is_blocked("user@x.com")
