"""Testes DOM-24: PATCH /api/v1/auth/change-password — alterar senha."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _create_user_token(client, db_session, email: str, password: str) -> str:
    """Cria conta e retorna token JWT."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash(password), role=UserRole.CUSTOMER)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": password}
    )
    return resp.json()["access_token"]


async def test_change_password_requer_auth(client) -> None:
    """PATCH /auth/change-password sem token retorna 401."""
    resp = await client.patch(
        "/api/v1/auth/change-password",
        json={"current_password": "senha", "new_password": "nova"},
    )
    assert resp.status_code == 401


async def test_change_password_senha_errada_retorna_422(client, db_session) -> None:
    """Senha atual incorreta retorna 422."""
    token = await _create_user_token(client, db_session, "cp_err@x.com", "correta")
    resp = await client.patch(
        "/api/v1/auth/change-password",
        json={"current_password": "errada", "new_password": "nova123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


async def test_change_password_ok(client, db_session) -> None:
    """Senha alterada com sucesso retorna 204 e login com nova senha funciona."""
    token = await _create_user_token(client, db_session, "cp_ok@x.com", "antiga")
    resp = await client.patch(
        "/api/v1/auth/change-password",
        json={"current_password": "antiga", "new_password": "nova_segura"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
    # Login com nova senha deve funcionar.
    login = await client.post(
        "/api/v1/auth/token",
        data={"username": "cp_ok@x.com", "password": "nova_segura"},
    )
    assert login.status_code == 200


async def test_change_password_senha_antiga_invalida_apos_troca(client, db_session) -> None:  # noqa: E501
    """Após alterar, login com senha antiga deve falhar."""
    token = await _create_user_token(client, db_session, "cp_old@x.com", "velha")
    await client.patch(
        "/api/v1/auth/change-password",
        json={"current_password": "velha", "new_password": "nova_senha"},
        headers={"Authorization": f"Bearer {token}"},
    )
    old_login = await client.post(
        "/api/v1/auth/token",
        data={"username": "cp_old@x.com", "password": "velha"},
    )
    assert old_login.status_code == 401
