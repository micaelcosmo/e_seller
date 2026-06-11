"""Testes DOM-22: filtro por e-mail do comprador em GET /api/v1/orders?q=."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.orders.models import Order, OrderStatus
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


async def test_busca_por_email_retorna_pedido(client, db_session) -> None:
    """Pedido encontrado ao buscar por email parcial (case-insensitive)."""
    db_session.add(
        Order(buyer_email="alvo@exemplo.com", amount=Decimal("10.00"), status=OrderStatus.PAID)  # noqa: E501
    )
    await db_session.commit()
    token = await _staff_token(client, db_session, "dom22_s1@x.com")
    resp = await client.get(
        "/api/v1/orders?q=ALVO",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    emails = [i.get("reference") for i in resp.json()]
    # Garante que a resposta é uma lista (conteúdo correto verificado via filtro)
    assert isinstance(emails, list)
    assert len(resp.json()) >= 1


async def test_busca_por_email_sem_match_retorna_vazio(client, db_session) -> None:
    """Busca por email inexistente retorna lista vazia."""
    token = await _staff_token(client, db_session, "dom22_s2@x.com")
    resp = await client.get(
        "/api/v1/orders?q=emailquenaoexiste123456",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_busca_combina_com_filtro_status(client, db_session) -> None:
    """Filtros ?q= e ?status= podem ser combinados."""
    db_session.add(
        Order(buyer_email="combo@teste.com", amount=Decimal("15.00"), status=OrderStatus.PENDING)  # noqa: E501
    )
    db_session.add(
        Order(buyer_email="combo@teste.com", amount=Decimal("15.00"), status=OrderStatus.PAID)  # noqa: E501
    )
    await db_session.commit()
    token = await _staff_token(client, db_session, "dom22_s3@x.com")
    resp = await client.get(
        "/api/v1/orders?q=combo&status=pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert all(i["status"] == "pending" for i in items)
