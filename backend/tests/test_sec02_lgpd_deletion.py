"""Testes de SEC-02/SEC-05: endpoint de exclusão LGPD (DELETE /api/v1/account).

Cobre: anonimização de e-mail, esvaziamento de dados pessoais, desativação
e preenchimento de deleted_at. O endpoint exige autenticação.
"""

from __future__ import annotations

from app.accounts.models import User


async def _make_user_and_token(client, db_session) -> tuple[str, int]:
    """Registra um usuário e retorna (token, user_id)."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "lgpd@test.com",
            "password": "pwd12345",
            "full_name": "LGPD Test",
        },
    )
    assert resp.status_code == 201
    token_resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "lgpd@test.com", "password": "pwd12345"},
    )
    token = token_resp.json()["access_token"]
    return token


async def test_delete_account_retorna_204(client, db_session):
    """DELETE /account com token válido retorna 204."""
    token = await _make_user_and_token(client, db_session)
    resp = await client.delete(
        "/api/v1/auth/account",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204


async def test_delete_account_anonimiza_email(client, db_session):
    """Após exclusão, o e-mail original não existe mais no banco."""
    from sqlalchemy import select

    token = await _make_user_and_token(client, db_session)
    await client.delete(
        "/api/v1/auth/account",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = await db_session.scalars(
        select(User).where(User.email == "lgpd@test.com")
    )
    assert result.first() is None


async def test_delete_account_preenche_deleted_at(client, db_session):
    """Após exclusão, User.deleted_at é preenchido."""
    from sqlalchemy import select

    token = await _make_user_and_token(client, db_session)
    await client.delete(
        "/api/v1/auth/account",
        headers={"Authorization": f"Bearer {token}"},
    )
    result = await db_session.scalars(
        select(User).where(User.email.like("deleted-%@anonymized.invalid"))
    )
    user = result.first()
    assert user is not None
    assert user.deleted_at is not None
    assert user.is_active is False


async def test_delete_account_sem_token_retorna_401(client):
    """DELETE /account sem token retorna 401."""
    resp = await client.delete("/api/v1/auth/account")
    assert resp.status_code == 401


async def test_delete_account_desativa_login(client, db_session):
    """Após exclusão, login com e-mail original falha (conta inexistente)."""
    token = await _make_user_and_token(client, db_session)
    await client.delete(
        "/api/v1/auth/account",
        headers={"Authorization": f"Bearer {token}"},
    )
    login_resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "lgpd@test.com", "password": "pwd12345"},
    )
    assert login_resp.status_code == 401
