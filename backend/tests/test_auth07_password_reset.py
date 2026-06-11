"""Testes AUTH-07 + SEC-15: fluxo de redefinição de senha por token JWT."""

from __future__ import annotations

import time

from app.accounts.models import User, UserRole
from app.core.config import get_settings
from app.security.jwt import JwtService
from app.security.passwords import PasswordHasher


async def _create_user(db_session, email: str = "reset@example.com") -> User:
    """Cria e persiste um usuário de teste."""
    settings = get_settings()
    hasher = PasswordHasher(settings.password_hash_iterations)
    user = User(
        email=email,
        password_hash=hasher.hash("senhaoriginal"),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


async def test_forgot_password_email_existente_retorna_200(client, db_session) -> None:
    """POST /forgot-password com e-mail válido retorna 200 e mensagem genérica."""
    await _create_user(db_session)
    resp = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "reset@example.com"}
    )
    assert resp.status_code == 200
    detail = resp.json()["detail"]
    assert "link" in detail.lower() or "receberá" in detail


async def test_forgot_password_email_inexistente_retorna_200(client) -> None:
    """POST /forgot-password com e-mail desconhecido retorna 200 — sem enumeração."""
    resp = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "naoexiste@example.com"}
    )
    assert resp.status_code == 200
    assert "receberá" in resp.json()["detail"]


async def test_reset_password_token_valido_altera_senha(client, db_session) -> None:
    """POST /reset-password com token válido altera a senha do usuário."""
    user = await _create_user(db_session, email="reset2@example.com")
    settings = get_settings()
    jwt = JwtService(
        secret_key=settings.app_secret_key,
        ttl_seconds=settings.jwt_ttl_seconds,
    )
    token = jwt.issue_reset(user.email)
    resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "novasenha456"},
    )
    assert resp.status_code == 204
    # Confirma novo login com a nova senha funciona
    login_resp = await client.post(
        "/api/v1/auth/token",
        data={"username": user.email, "password": "novasenha456"},
    )
    assert login_resp.status_code == 200


async def test_reset_password_token_invalido_retorna_400(client) -> None:
    """POST /reset-password com token adulterado retorna 400."""
    resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": "token.invalido.assinatura", "new_password": "qualquer"},
    )
    assert resp.status_code == 400


async def test_reset_password_token_expirado_retorna_400(client, db_session) -> None:
    """POST /reset-password com token expirado retorna 400."""
    user = await _create_user(db_session, email="reset3@example.com")
    settings = get_settings()
    jwt = JwtService(
        secret_key=settings.app_secret_key,
        ttl_seconds=settings.jwt_ttl_seconds,
    )
    # Emite token com `now` no passado suficiente para expirar
    past = int(time.time()) - 7200
    token = jwt.issue_reset(user.email, now=past)
    resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "qualquer123"},
    )
    assert resp.status_code == 400
