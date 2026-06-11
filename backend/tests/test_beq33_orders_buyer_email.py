"""Testes BEQ-33: filtro ?buyer_email= na listagem admin de pedidos."""

from __future__ import annotations

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


async def test_filtra_por_buyer_email(client, db_session) -> None:
    """?buyer_email= deve retornar apenas pedidos do comprador indicado."""
    o1 = Order(
        reference="BEQ33-A1",
        buyer_email="alice@beq33.com",
        amount=10,
        status=OrderStatus.PAID,
    )
    o2 = Order(
        reference="BEQ33-B1",
        buyer_email="bob@beq33.com",
        amount=20,
        status=OrderStatus.PAID,
    )
    db_session.add_all([o1, o2])
    await db_session.commit()

    token = await _staff_token(client, db_session, "beq33staff@x.com")
    resp = await client.get(
        "/api/v1/orders?buyer_email=alice",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    refs = {item["reference"] for item in items}
    assert "BEQ33-A1" in refs
    assert "BEQ33-B1" not in refs


async def test_buyer_email_prevalece_sobre_q(client, db_session) -> None:
    """Se ambos ?buyer_email= e ?q= forem passados, buyer_email prevalece."""
    o1 = Order(
        reference="BEQ33-C1",
        buyer_email="carol@beq33.com",
        amount=30,
        status=OrderStatus.PENDING,
    )
    o2 = Order(
        reference="BEQ33-D1",
        buyer_email="dave@beq33.com",
        amount=40,
        status=OrderStatus.PENDING,
    )
    db_session.add_all([o1, o2])
    await db_session.commit()

    token = await _staff_token(client, db_session, "beq33b_staff@x.com")
    resp = await client.get(
        "/api/v1/orders?buyer_email=carol&q=dave",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    refs = {item["reference"] for item in items}
    assert "BEQ33-C1" in refs
    assert "BEQ33-D1" not in refs


async def test_x_total_count_com_buyer_email_filter(client, db_session) -> None:
    """X-Total-Count deve refletir apenas os pedidos do comprador filtrado."""
    o1 = Order(
        reference="BEQ33-E1",
        buyer_email="eve@beq33.com",
        amount=50,
        status=OrderStatus.PAID,
    )
    o2 = Order(
        reference="BEQ33-F1",
        buyer_email="frank@beq33.com",
        amount=60,
        status=OrderStatus.PAID,
    )
    db_session.add_all([o1, o2])
    await db_session.commit()

    token = await _staff_token(client, db_session, "beq33c_staff@x.com")
    resp = await client.get(
        "/api/v1/orders?buyer_email=eve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert int(resp.headers["x-total-count"]) == 1
