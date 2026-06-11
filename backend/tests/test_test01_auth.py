"""Testes TEST-01: cobertura adicional de JWT/login/permissões."""

from __future__ import annotations

import pytest

from app.accounts.models import User, UserRole
from app.security.jwt import InvalidToken, JwtService
from app.security.passwords import PasswordHasher


async def test_login_credenciais_invalidas(client, db_session):
    """Login com senha errada retorna 401."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="t1@x.com",
            password_hash=hasher.hash("certa"),
            role=UserRole.CUSTOMER,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": "t1@x.com", "password": "errada"}
    )
    assert resp.status_code == 401


async def test_login_usuario_inativo(client, db_session):
    """Usuário inativo não consegue login (401)."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="inativo@x.com",
            password_hash=hasher.hash("pw"),
            is_active=False,
            role=UserRole.CUSTOMER,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": "inativo@x.com", "password": "pw"}
    )
    assert resp.status_code == 401


def test_jwt_expirado_retorna_invalido_token():
    """Token com exp no passado levanta InvalidToken."""
    svc = JwtService(secret_key="seg", ttl_seconds=1)
    token = svc.issue("u@e.com", now=0)
    with pytest.raises(InvalidToken):
        svc.verify(token, now=10)


def test_jwt_secret_errado_retorna_invalido_token():
    """Token gerado com segredo diferente levanta InvalidToken."""
    svc_a = JwtService(secret_key="a", ttl_seconds=3600)
    svc_b = JwtService(secret_key="b", ttl_seconds=3600)
    token = svc_a.issue("u@e.com")
    with pytest.raises(InvalidToken):
        svc_b.verify(token)


async def test_me_com_token_valido(client, db_session):
    """GET /me com token válido retorna email e papel."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email="me@x.com", password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER)
    )
    await db_session.commit()
    login = await client.post(
        "/api/v1/auth/token", data={"username": "me@x.com", "password": "pw"}
    )
    token = login.json()["access_token"]
    resp = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@x.com"


async def test_register_email_duplicado(client, db_session):
    """Registrar com e-mail já usado retorna 409."""
    payload = {"email": "dup@x.com", "password": "pw123"}
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409
