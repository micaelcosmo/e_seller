"""Testes BEQ-21: PATCH /api/v1/admin/auth/users/{id}/toggle-active."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token JWT."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_toggle_requer_staff(client) -> None:
    """PATCH sem token retorna 401."""
    resp = await client.patch("/api/v1/admin/auth/users/1/toggle-active")
    assert resp.status_code == 401


async def test_toggle_inexistente_retorna_404(client, db_session) -> None:
    """Usuário inexistente retorna 404."""
    token = await _staff_token(client, db_session, "beq21_s1@x.com")
    resp = await client.patch(
        "/api/v1/admin/auth/users/999999/toggle-active",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_toggle_desativa_usuario_ativo(client, db_session) -> None:
    """Toggle em usuário ativo o desativa."""
    hasher = PasswordHasher(iterations=1000)
    user = User(email="alvo1@x.com", password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER, is_active=True)  # noqa: E501
    db_session.add(user)
    await db_session.commit()
    token = await _staff_token(client, db_session, "beq21_s2@x.com")
    resp = await client.patch(
        f"/api/v1/admin/auth/users/{user.id}/toggle-active",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_toggle_ativa_usuario_inativo(client, db_session) -> None:
    """Toggle em usuário inativo o ativa."""
    hasher = PasswordHasher(iterations=1000)
    user = User(email="alvo2@x.com", password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER, is_active=False)  # noqa: E501
    db_session.add(user)
    await db_session.commit()
    token = await _staff_token(client, db_session, "beq21_s3@x.com")
    resp = await client.patch(
        f"/api/v1/admin/auth/users/{user.id}/toggle-active",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is True
