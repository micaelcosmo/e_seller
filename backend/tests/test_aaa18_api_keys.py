"""Testes de API Keys (AAA-14..18): criação, autenticação, revogação, ownership."""

import pytest

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _make_user_and_login(client, db_session, email: str) -> str:
    """Cria usuário de teste (hasher rápido) e retorna o access_token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw123"), role=UserRole.CUSTOMER)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "pw123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_api_key_returns_raw_key(client, db_session):
    """APIKEY-001: criar API Key retorna chave crua; listagem não a expõe."""
    token = await _make_user_and_login(client, db_session, "ak001@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/auth/me/api-keys",
        json={"name": "minha-key"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    data = create_resp.json()
    assert "key" in data and data["key"]
    assert "prefix" in data

    list_resp = await client.get("/api/v1/auth/me/api-keys", headers=headers)
    assert list_resp.status_code == 200
    for k in list_resp.json():
        assert "key" not in k


@pytest.mark.asyncio
async def test_authenticate_via_api_key(client, db_session):
    """APIKEY-002: autenticação via X-API-Key funciona."""
    jwt_token = await _make_user_and_login(client, db_session, "ak002@test.com")
    create_resp = await client.post(
        "/api/v1/auth/me/api-keys",
        json={"name": "auto-test"},
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    raw_key = create_resp.json()["key"]

    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"X-API-Key": raw_key},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "ak002@test.com"


@pytest.mark.asyncio
async def test_invalid_api_key_returns_401(client):
    """APIKEY-003: chave inválida retorna 401."""
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"X-API-Key": "sk_invalida123456789"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_revoked_api_key_returns_401(client, db_session):
    """APIKEY-004: chave revogada não autentica mais."""
    jwt_token = await _make_user_and_login(client, db_session, "ak004@test.com")
    headers = {"Authorization": f"Bearer {jwt_token}"}

    create_resp = await client.post(
        "/api/v1/auth/me/api-keys",
        json={"name": "revoke-test"},
        headers=headers,
    )
    raw_key = create_resp.json()["key"]
    key_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/v1/auth/me/api-keys/{key_id}", headers=headers
    )
    assert del_resp.status_code == 204

    resp_after = await client.get(
        "/api/v1/auth/me",
        headers={"X-API-Key": raw_key},
    )
    assert resp_after.status_code == 401
