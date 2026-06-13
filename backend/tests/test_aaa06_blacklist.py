"""Testes do token blacklist (AAA-01..06): logout revoga JWT, jti presente, isolamento."""

import pytest

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _make_user_and_login(client, db_session, email: str) -> str:
    """Cria um usuário de teste (hasher rápido) e retorna o access_token."""
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
async def test_token_has_jti(client, db_session):
    """BL-004: access_token emitido contém claim jti."""
    import base64
    import json

    token = await _make_user_and_login(client, db_session, "bl004@test.com")
    parts = token.split(".")
    assert len(parts) == 3
    padding = "=" * (-len(parts[1]) % 4)
    payload = json.loads(base64.urlsafe_b64decode(parts[1] + padding))
    assert "jti" in payload and payload["jti"]


@pytest.mark.asyncio
async def test_logout_revokes_token(client, db_session):
    """BL-001: token revogado retorna 401 em endpoint protegido."""
    token = await _make_user_and_login(client, db_session, "bl001@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200

    logout = await client.post("/api/v1/auth/logout", headers=headers)
    assert logout.status_code == 204

    resp_after = await client.get("/api/v1/auth/me", headers=headers)
    assert resp_after.status_code == 401


@pytest.mark.asyncio
async def test_logout_without_token_returns_401(client):
    """BL-002: logout sem Bearer token retorna 401."""
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_does_not_affect_other_user(client, db_session):
    """BL-003: logout de user_A não invalida token de user_B."""
    token_a = await _make_user_and_login(client, db_session, "bl003a@test.com")
    token_b = await _make_user_and_login(client, db_session, "bl003b@test.com")

    await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    resp_b = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_b.status_code == 200
