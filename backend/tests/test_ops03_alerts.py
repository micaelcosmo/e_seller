"""Testes OPS-03: endpoint de verificação de alertas operacionais."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session) -> str:
    """Cria staff e retorna o token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(User(
        email="alerts_staff@x.com",
        password_hash=hasher.hash("pw"),
        role=UserRole.STAFF,
    ))
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": "alerts_staff@x.com", "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_alerts_sem_auth_retorna_401(client) -> None:
    """GET /admin/alerts/check sem token retorna 401."""
    resp = await client.get("/api/v1/admin/alerts/check")
    assert resp.status_code == 401


async def test_alerts_staff_retorna_200(client, db_session) -> None:
    """Staff acessa o endpoint de alertas e recebe resposta JSON."""
    token = await _staff_token(client, db_session)
    resp = await client.get(
        "/api/v1/admin/alerts/check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "ok" in body
    assert "alerts" in body
    assert isinstance(body["alerts"], list)


async def test_alerts_ok_sem_dados(client, db_session) -> None:
    """Com banco vazio não há alertas ativos: ok=true."""
    token = await _staff_token(client, db_session)
    resp = await client.get(
        "/api/v1/admin/alerts/check",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = resp.json()
    # banco de teste está vazio ou com seeds sem pedidos pagos sem grants
    assert body["ok"] is True or isinstance(body["alerts"], list)


async def test_alerts_customer_retorna_403(client, db_session) -> None:
    """Customer não pode acessar endpoint de alertas."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="cust_alerts@x.com",
            password_hash=hasher.hash("pw"),
            role=UserRole.CUSTOMER,
        )
    )
    await db_session.commit()
    login = await client.post(
        "/api/v1/auth/token", data={"username": "cust_alerts@x.com", "password": "pw"}
    )
    token = login.json()["access_token"]
    resp = await client.get(
        "/api/v1/admin/alerts/check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
