"""Testes TEST-02: permissões do painel admin e endpoints de staff."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _make_user(db_session, email: str, role: UserRole) -> str:
    """Cria usuário, faz login e retorna o access_token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw123"), role=role)
    )
    await db_session.commit()
    return email


async def _login(client, email: str) -> str:
    """Autentica e retorna o token de acesso."""
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw123"}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


async def test_status_panel_sem_auth_retorna_401(client) -> None:
    """GET /admin/products/status-panel sem token retorna 401."""
    resp = await client.get("/api/v1/admin/products/status-panel")
    assert resp.status_code == 401


async def test_status_panel_customer_retorna_403(client, db_session) -> None:
    """Customer não pode acessar painel de status (403)."""
    await _make_user(db_session, "cust@x.com", UserRole.CUSTOMER)
    token = await _login(client, "cust@x.com")
    resp = await client.get(
        "/api/v1/admin/products/status-panel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


async def test_status_panel_staff_retorna_200(client, db_session) -> None:
    """Staff acessa o painel de status com 200 e recebe HTML."""
    await _make_user(db_session, "staff@x.com", UserRole.STAFF)
    token = await _login(client, "staff@x.com")
    resp = await client.get(
        "/api/v1/admin/products/status-panel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


async def test_create_product_sem_auth_retorna_401(client) -> None:
    """POST /admin/products sem token retorna 401."""
    resp = await client.post(
        "/api/v1/admin/products",
        json={"title": "Novo E-book", "price": "29.90"},
    )
    assert resp.status_code == 401


async def test_create_product_admin_retorna_201(client, db_session) -> None:
    """Admin consegue cadastrar e-book (201)."""
    await _make_user(db_session, "admin2@x.com", UserRole.ADMIN)
    token = await _login(client, "admin2@x.com")
    resp = await client.post(
        "/api/v1/admin/products",
        json={"title": "E-book Admin", "price": "15.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "E-book Admin"
