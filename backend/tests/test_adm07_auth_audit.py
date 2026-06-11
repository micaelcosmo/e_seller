"""Testes ADM-07: listagem admin de tentativas de login."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria staff e retorna token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_listagem_attempts_requer_auth(client) -> None:
    """GET /admin/auth/attempts sem token retorna 401."""
    resp = await client.get("/api/v1/admin/auth/attempts")
    assert resp.status_code == 401


async def test_listagem_attempts_staff_ok(client, db_session) -> None:
    """Staff obtém lista de tentativas de login."""
    token = await _staff_token(client, db_session, "adm7_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/auth/attempts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    # Deve ter pelo menos a tentativa de login do próprio setup.
    assert len(items) >= 1


async def test_filtro_only_failures(client, db_session) -> None:
    """Filtro only_failures=true retorna apenas falhas."""
    token = await _staff_token(client, db_session, "adm7_staff2@x.com")
    # Gera uma falha de login.
    await client.post(
        "/api/v1/auth/token",
        data={"username": "nobody@x.com", "password": "wrong"},
    )
    resp = await client.get(
        "/api/v1/admin/auth/attempts?only_failures=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    for item in items:
        assert item["success"] is False, "Item com success=True em filtro de falhas."
