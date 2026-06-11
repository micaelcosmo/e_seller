"""Testes BEQ-10: endpoint admin de listagem de pedidos (paginado + filtro)."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _make_staff_token(client, db_session, email: str) -> str:
    """Cria usuário staff e retorna token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def _make_customer_token(client, db_session, email: str) -> str:
    """Cria usuário customer e retorna token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_listagem_pedidos_requer_autenticacao(client) -> None:
    """GET /orders sem token retorna 401."""
    resp = await client.get("/api/v1/orders")
    assert resp.status_code == 401


async def test_listagem_pedidos_requer_staff(client, db_session) -> None:
    """GET /orders com token de customer retorna 403."""
    token = await _make_customer_token(client, db_session, "ord_cust@x.com")
    resp = await client.get(
        "/api/v1/orders", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403


async def test_listagem_pedidos_admin_retorna_lista(client, db_session) -> None:
    """Staff obtém lista de pedidos (pode ser vazia antes de criar pedidos)."""
    token = await _make_staff_token(client, db_session, "ord_staff@x.com")
    resp = await client.get(
        "/api/v1/orders", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_listagem_pedidos_filtro_status_invalido(client, db_session) -> None:
    """Filtro por status inexistente retorna lista vazia (sem erro)."""
    token = await _make_staff_token(client, db_session, "ord_staff2@x.com")
    resp = await client.get(
        "/api/v1/orders?status=xpto",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_listagem_pedidos_paginacao(client, db_session) -> None:
    """Parâmetros page e page_size são aceitos sem erro."""
    token = await _make_staff_token(client, db_session, "ord_staff3@x.com")
    resp = await client.get(
        "/api/v1/orders?page=1&page_size=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
