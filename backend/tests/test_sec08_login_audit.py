"""Testes SEC-08: auditoria de tentativas de login."""

from __future__ import annotations

from sqlalchemy import select

from app.accounts.models import LoginAttempt, User, UserRole
from app.security.passwords import PasswordHasher


async def test_login_sucesso_registrado(client, db_session) -> None:
    """Após login bem-sucedido, LoginAttempt success=True deve existir no DB."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="audit_ok@x.com",
            password_hash=hasher.hash("pw"),
            role=UserRole.CUSTOMER,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "audit_ok@x.com", "password": "pw"},
    )
    assert resp.status_code == 200
    result = await db_session.scalars(
        select(LoginAttempt).where(
            LoginAttempt.email == "audit_ok@x.com",
            LoginAttempt.success.is_(True),
        )
    )
    assert result.first() is not None, "Tentativa de login bem-sucedida não registrada."


async def test_login_falha_registrado(client, db_session) -> None:
    """Após login com senha errada, LoginAttempt success=False deve existir."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="audit_fail@x.com",
            password_hash=hasher.hash("correta"),
            role=UserRole.CUSTOMER,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "audit_fail@x.com", "password": "errada"},
    )
    assert resp.status_code == 401
    result = await db_session.scalars(
        select(LoginAttempt).where(
            LoginAttempt.email == "audit_fail@x.com",
            LoginAttempt.success.is_(False),
        )
    )
    assert result.first() is not None, "Tentativa de login falha não registrada."


async def test_login_usuario_inexistente_registrado(client, db_session) -> None:
    """Login com email que não existe também gera um LoginAttempt de falha."""
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "ghost@x.com", "password": "qualquer"},
    )
    assert resp.status_code == 401
    result = await db_session.scalars(
        select(LoginAttempt).where(LoginAttempt.email == "ghost@x.com")
    )
    assert result.first() is not None, "Tentativa com email inexistente não registrada."
