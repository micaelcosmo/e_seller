"""Testes ADM-06: listagem admin de estornos."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria staff e retorna token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_lista_estornos_requer_autenticacao(client) -> None:
    """GET /admin/refunds sem token retorna 401."""
    resp = await client.get("/api/v1/admin/refunds")
    assert resp.status_code == 401


async def test_lista_estornos_staff_retorna_lista(client, db_session) -> None:
    """Staff obtém lista de estornos (vazia antes de estornar)."""
    token = await _staff_token(client, db_session, "ref_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/refunds",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_lista_estornos_paginacao(client, db_session) -> None:
    """Parâmetros page e page_size são aceitos sem erro."""
    token = await _staff_token(client, db_session, "ref_staff2@x.com")
    resp = await client.get(
        "/api/v1/admin/refunds?page=1&page_size=5",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
