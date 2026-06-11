"""Testes de OPS-02: endpoint /metrics com KPIs operacionais."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _admin_token(client, db_session) -> str:
    """Cria admin e retorna token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="ops_admin@x.com",
            password_hash=hasher.hash("pw1234"),
            role=UserRole.ADMIN,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "ops_admin@x.com", "password": "pw1234"},
    )
    return resp.json()["access_token"]


async def test_metrics_retorna_estrutura_esperada(client, db_session):
    """GET /metrics retorna produtos, usuários, pedidos e receita."""
    token = await _admin_token(client, db_session)
    resp = await client.get(
        "/api/v1/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "products" in data
    assert "users" in data
    assert "orders" in data
    assert "revenue" in data


async def test_metrics_produtos_tem_campos(client, db_session):
    """Subchave 'products' contém total, published e draft."""
    token = await _admin_token(client, db_session)
    resp = await client.get(
        "/api/v1/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )
    products = resp.json()["products"]
    assert "total" in products
    assert "published" in products
    assert "draft" in products


async def test_metrics_sem_token_retorna_401(client):
    """GET /metrics sem token retorna 401."""
    resp = await client.get("/api/v1/metrics")
    assert resp.status_code == 401


async def test_metrics_usuario_comum_retorna_403(client, db_session):
    """GET /metrics com papel customer retorna 403."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="cust_metrics@x.com",
            password_hash=hasher.hash("pw1234"),
            role=UserRole.CUSTOMER,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "cust_metrics@x.com", "password": "pw1234"},
    )
    token = resp.json()["access_token"]
    resp2 = await client.get(
        "/api/v1/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 403


async def test_reports_sem_token_retorna_401(client):
    """GET /admin/reports/sales sem token retorna 401."""
    resp = await client.get(
        "/api/v1/admin/reports/sales?date_from=2026-01-01&date_to=2026-12-31"
    )
    assert resp.status_code == 401
