"""Testes OPS-22: header X-Export-Limit no export CSV de pedidos."""

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


async def test_export_csv_inclui_header_x_export_limit(
    client, db_session
) -> None:
    """GET /orders/export deve incluir header X-Export-Limit com valor numérico."""
    token = await _staff_token(client, db_session, "ops22_a@x.com")
    resp = await client.get(
        "/api/v1/orders/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "x-export-limit" in resp.headers
    assert int(resp.headers["x-export-limit"]) == 10000


async def test_export_csv_content_type_correto(client, db_session) -> None:
    """Export CSV deve retornar content-type text/csv."""
    token = await _staff_token(client, db_session, "ops22_b@x.com")
    resp = await client.get(
        "/api/v1/orders/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
