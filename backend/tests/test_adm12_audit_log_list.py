"""Testes ADM-12: listagem do audit log administrativo."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.admin.audit import AdminAuditService
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


async def test_audit_log_retorna_x_total_count(client, db_session) -> None:
    """GET /admin/audit-log deve retornar header X-Total-Count."""
    service = AdminAuditService(db_session)
    await service.log("adm12@test.com", "create", "product", "1")
    await db_session.commit()
    token = await _staff_token(client, db_session, "adm12_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/audit-log",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "x-total-count" in resp.headers
    assert int(resp.headers["x-total-count"]) >= 1


async def test_audit_log_filtra_por_action(client, db_session) -> None:
    """Filtro ?action= deve retornar apenas entradas com aquela ação."""
    service = AdminAuditService(db_session)
    await service.log("adm12b@test.com", "delete", "coupon", "CODE1")
    await service.log("adm12b@test.com", "create", "coupon", "CODE2")
    await db_session.commit()
    token = await _staff_token(client, db_session, "adm12b_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/audit-log?action=delete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    for item in items:
        assert item["action"] == "delete"


async def test_audit_log_requer_autenticacao(client) -> None:
    """GET /admin/audit-log sem token deve retornar 401."""
    resp = await client.get("/api/v1/admin/audit-log")
    assert resp.status_code == 401
