"""Testes DOM-30: POST /orders/my/{ref}/cancel — cancelamento de pedido pelo comprador."""  # noqa: E501

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.orders.models import Order, OrderStatus
from app.security.passwords import PasswordHasher


async def _buyer_token(client, db_session, email: str) -> tuple[str, User]:
    """Cria conta comprador e retorna (token, user)."""
    hasher = PasswordHasher(iterations=1000)
    user = User(
        email=email, password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER
    )
    db_session.add(user)
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"], user


async def test_cancelar_pedido_pending(client, db_session) -> None:
    """Comprador pode cancelar pedido PENDING."""
    token, user = await _buyer_token(client, db_session, "cancel1@x.com")
    order = Order(
        buyer_email="cancel1@x.com",
        amount=Decimal("29.90"),
        status=OrderStatus.PENDING,
        user_id=user.id,
    )
    db_session.add(order)
    await db_session.commit()
    resp = await client.post(
        f"/api/v1/orders/my/{order.reference}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_cancelar_pedido_pago_retorna_409(client, db_session) -> None:
    """Tentar cancelar pedido PAID retorna 409."""
    token, user = await _buyer_token(client, db_session, "cancel2@x.com")
    order = Order(
        buyer_email="cancel2@x.com",
        amount=Decimal("29.90"),
        status=OrderStatus.PAID,
        user_id=user.id,
    )
    db_session.add(order)
    await db_session.commit()
    resp = await client.post(
        f"/api/v1/orders/my/{order.reference}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409


async def test_cancelar_pedido_de_outro_usuario_retorna_404(client, db_session) -> None:
    """Referência de pedido de outro usuário retorna 404."""
    token, _own_user = await _buyer_token(client, db_session, "cancel3@x.com")
    other_order = Order(
        buyer_email="outro@x.com",
        amount=Decimal("29.90"),
        status=OrderStatus.PENDING,
        user_id=9999,
    )
    db_session.add(other_order)
    await db_session.commit()
    resp = await client.post(
        f"/api/v1/orders/my/{other_order.reference}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
