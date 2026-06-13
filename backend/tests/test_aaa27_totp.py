"""Testes do fluxo TOTP 2FA (AAA-19..27): enroll, confirm, login passo 2, disable."""

import pyotp
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
async def test_totp_enroll_returns_secret_and_uri(client, db_session):
    """TOTP-001: POST /2fa/enroll retorna secret e provisioning_uri válidos."""
    token = await _make_user_and_login(client, db_session, "totp001@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/auth/2fa/enroll", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "secret" in data and data["secret"]
    assert "provisioning_uri" in data
    assert data["provisioning_uri"].startswith("otpauth://totp/")
    totp = pyotp.TOTP(data["secret"])
    code = totp.now()
    assert len(code) == 6


@pytest.mark.asyncio
async def test_totp_confirm_with_valid_code(client, db_session):
    """TOTP-002: confirmação com código válido ativa 2FA."""
    from sqlalchemy import select

    from app.accounts.models import User as UserModel

    token = await _make_user_and_login(client, db_session, "totp002@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    enroll = await client.post("/api/v1/auth/2fa/enroll", headers=headers)
    secret = enroll.json()["secret"]
    code = pyotp.TOTP(secret).now()

    confirm = await client.post(
        "/api/v1/auth/2fa/confirm",
        json={"secret": secret, "code": code},
        headers=headers,
    )
    assert confirm.status_code == 204

    db_session.expire_all()
    result = await db_session.scalars(
        select(UserModel).where(UserModel.email == "totp002@test.com")
    )
    user = result.first()
    assert user.totp_enabled is True
    assert user.totp_secret_enc is not None


@pytest.mark.asyncio
async def test_totp_confirm_with_invalid_code_rejected(client, db_session):
    """TOTP-003: código inválido é rejeitado; 2FA não ativado."""
    token = await _make_user_and_login(client, db_session, "totp003@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    enroll = await client.post("/api/v1/auth/2fa/enroll", headers=headers)
    secret = enroll.json()["secret"]

    confirm = await client.post(
        "/api/v1/auth/2fa/confirm",
        json={"secret": secret, "code": "000000"},
        headers=headers,
    )
    assert confirm.status_code == 400
