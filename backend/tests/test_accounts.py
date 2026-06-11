"""Testes de contas: registro, login, perfil e autorização por papel (RBAC)."""

import pytest
from fastapi import HTTPException

from app.accounts.models import User, UserRole
from app.security.deps import RequireRole


async def test_registro_e_login_e_perfil(client):
    """Registrar comprador, logar e obter o perfil pelo token."""
    registro = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "comprador@x.com",
            "password": "senha123",
            "full_name": "Fulano",
        },
    )
    assert registro.status_code == 201
    assert registro.json()["role"] == "customer"

    login = await client.post(
        "/api/v1/auth/token",
        data={"username": "comprador@x.com", "password": "senha123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    perfil = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert perfil.status_code == 200
    assert perfil.json()["email"] == "comprador@x.com"


async def test_login_invalido_retorna_401(client):
    """Credenciais inválidas retornam 401."""
    login = await client.post(
        "/api/v1/auth/token",
        data={"username": "naoexiste@x.com", "password": "x"},
    )
    assert login.status_code == 401


async def test_registro_duplicado_retorna_409(client):
    """Registrar um e-mail já usado retorna 409."""
    payload = {"email": "dup@x.com", "password": "123456"}
    await client.post("/api/v1/auth/register", json=payload)
    segundo = await client.post("/api/v1/auth/register", json=payload)
    assert segundo.status_code == 409


async def test_me_sem_token_retorna_401(client):
    """Acessar o perfil sem token retorna 401."""
    perfil = await client.get("/api/v1/auth/me")
    assert perfil.status_code == 401


def test_require_role_permite_papel_correto():
    """RequireRole libera o acesso quando o papel é permitido."""
    user = User(email="a@x.com", password_hash="x", role=UserRole.ADMIN)
    assert RequireRole("admin", "staff")(user=user) is user


def test_require_role_nega_papel_insuficiente():
    """RequireRole nega (403) quando o papel não é permitido."""
    user = User(email="c@x.com", password_hash="x", role=UserRole.CUSTOMER)
    with pytest.raises(HTTPException) as exc:
        RequireRole("admin")(user=user)
    assert exc.value.status_code == 403
