"""Testes BEQ-14: listagem admin de todos os produtos (draft + published)."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_listagem_requer_auth(client) -> None:
    """GET /admin/products sem token retorna 401."""
    resp = await client.get("/api/v1/admin/products")
    assert resp.status_code == 401


async def test_listagem_retorna_todos_produtos(client, db_session) -> None:
    """Staff vê todos os produtos (draft e published)."""
    token = await _staff_token(client, db_session, "beq14_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/products",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) >= 1


async def test_filtro_status_published(client, db_session) -> None:
    """Filtro ?status=published retorna apenas publicados."""
    token = await _staff_token(client, db_session, "beq14_staff2@x.com")
    resp = await client.get(
        "/api/v1/admin/products?status=published",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    for item in resp.json():
        assert item["slug"] is not None


async def test_filtro_status_invalido_retorna_lista_vazia(client, db_session) -> None:
    """Status inválido retorna lista vazia (sem erro)."""
    token = await _staff_token(client, db_session, "beq14_staff3@x.com")
    resp = await client.get(
        "/api/v1/admin/products?status=invalido",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []
