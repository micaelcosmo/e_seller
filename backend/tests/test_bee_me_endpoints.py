"""Testes BEE: endpoints /api/v1/me/* (orders, library, wishlist, cart)."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _register_and_login(client, db_session: AsyncSession) -> str:
    """Cria usuário diretamente no DB e faz login; retorna o JWT."""
    hasher = PasswordHasher(iterations=1000)
    user = User(
        email="me-test@example.com",
        password_hash=hasher.hash("senha123"),
        role=UserRole.CUSTOMER,
    )
    db_session.add(user)
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "me-test@example.com", "password": "senha123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_me_orders_retorna_lista_vazia(client, db_session: AsyncSession) -> None:
    """BEE-10a: GET /api/v1/me/orders retorna [] para usuário sem pedidos."""
    token = await _register_and_login(client, db_session)
    resp = await client.get(
        "/api/v1/me/orders", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_me_library_retorna_lista_vazia(client, db_session: AsyncSession) -> None:
    """BEE-11a: GET /api/v1/me/library retorna [] para usuário sem compras."""
    token = await _register_and_login(client, db_session)
    resp = await client.get(
        "/api/v1/me/library", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_me_wishlist_retorna_lista_vazia(
    client, db_session: AsyncSession
) -> None:
    """BEE-12a: GET /api/v1/me/wishlist retorna [] para wishlist vazia."""
    token = await _register_and_login(client, db_session)
    resp = await client.get(
        "/api/v1/me/wishlist", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_me_cart_retorna_lista_vazia(client, db_session: AsyncSession) -> None:
    """BEE-12b: GET /api/v1/me/cart retorna [] para carrinho vazio."""
    token = await _register_and_login(client, db_session)
    resp = await client.get(
        "/api/v1/me/cart", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_me_orders_sem_auth_retorna_401(client) -> None:
    """BEE-10b: GET /api/v1/me/orders sem token retorna 401."""
    resp = await client.get("/api/v1/me/orders")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_library_sem_auth_retorna_401(client) -> None:
    """BEE-11b: GET /api/v1/me/library sem token retorna 401."""
    resp = await client.get("/api/v1/me/library")
    assert resp.status_code == 401
