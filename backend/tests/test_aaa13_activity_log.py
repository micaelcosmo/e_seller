"""Testes do UserActivityLog (AAA-07..13): login gera log, /me/activity isolado."""

import pytest


async def _register_and_login(client, email: str, password: str = "senha1234") -> str:
    """Registra um usuário e retorna o access_token."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test"},
    )
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_login_generates_activity_log(client, db_session):
    """ACT-001: login bem-sucedido cria entrada em UserActivityLog."""
    from sqlalchemy import select

    from app.accounts.models import UserActivityLog

    token = await _register_and_login(client, "act001@test.com")
    assert token

    result = await db_session.scalars(
        select(UserActivityLog).where(UserActivityLog.event_type == "login")
    )
    entries = list(result.all())
    assert len(entries) >= 1
    assert entries[-1].event_type == "login"


@pytest.mark.asyncio
async def test_me_activity_returns_own_entries_only(client, db_session):
    """ACT-005: GET /me/activity retorna apenas entradas do usuário autenticado."""
    from sqlalchemy import select

    from app.accounts.models import User
    from app.accounts.services_aaa import UserActivityLogService

    token_a = await _register_and_login(client, "act005a@test.com")
    await _register_and_login(client, "act005b@test.com")

    result = await db_session.scalars(
        select(User).where(User.email == "act005a@test.com")
    )
    user_a = result.first()
    svc = UserActivityLogService(db_session)
    await svc.log("purchase", user_id=user_a.id, order_ref="REF-TEST")

    resp = await client.get(
        "/api/v1/auth/me/activity",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for entry in data:
        assert entry["event_type"] in ("login", "purchase")


@pytest.mark.asyncio
async def test_me_activity_pagination(client, db_session):
    """ACT-006: GET /me/activity?limit=2 retorna no máximo 2 registros."""
    from sqlalchemy import select

    from app.accounts.models import User
    from app.accounts.services_aaa import UserActivityLogService

    token = await _register_and_login(client, "act006@test.com")
    result = await db_session.scalars(
        select(User).where(User.email == "act006@test.com")
    )
    user = result.first()
    svc = UserActivityLogService(db_session)
    for i in range(5):
        await svc.log("purchase", user_id=user.id, order_ref=f"REF-{i}")

    resp = await client.get(
        "/api/v1/auth/me/activity?limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) <= 2
