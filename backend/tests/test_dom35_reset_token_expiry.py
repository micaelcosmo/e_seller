"""Testes DOM-35: expiração de tokens de redefinição de senha."""

from __future__ import annotations

import time

from app.core.config import get_settings
from app.security.jwt import ExpiredToken, JwtService


def _make_jwt_service() -> JwtService:
    """Cria serviço JWT com a chave das settings de teste."""
    settings = get_settings()
    return JwtService(settings.app_secret_key)


async def test_token_reset_expirado_levanta_expired_token() -> None:
    """verify_reset com token cujo exp está no passado deve levantar ExpiredToken."""
    jwt = _make_jwt_service()
    past_now = int(time.time()) - 7200
    token = jwt.issue_reset("usuario@dom35.com", now=past_now)
    try:
        jwt.verify_reset(token)
        raise AssertionError("Deveria ter levantado ExpiredToken")
    except ExpiredToken:
        pass


async def test_token_reset_valido_retorna_email() -> None:
    """verify_reset com token válido deve retornar o e-mail do subject."""
    jwt = _make_jwt_service()
    token = jwt.issue_reset("usuario@dom35.com")
    email = jwt.verify_reset(token)
    assert email == "usuario@dom35.com"


async def test_post_reset_password_token_expirado_retorna_400(client) -> None:
    """POST /reset-password com token expirado deve retornar 400."""
    settings = get_settings()
    jwt = JwtService(settings.app_secret_key)
    past_now = int(time.time()) - 7200
    expired_token = jwt.issue_reset("naoexiste@dom35.com", now=past_now)
    resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": expired_token, "new_password": "novaSenha123"},
    )
    assert resp.status_code == 400
