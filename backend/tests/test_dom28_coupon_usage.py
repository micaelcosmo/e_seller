"""Testes DOM-28: GET /api/v1/admin/coupons/{code}/usage — histórico de resgates."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.coupons.models import Coupon, CouponRedemption, DiscountType
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


async def test_usage_404_cupom_inexistente(client, db_session) -> None:
    """Código não existente retorna 404."""
    token = await _staff_token(client, db_session, "dom28_s1@x.com")
    resp = await client.get(
        "/api/v1/admin/coupons/NAOEXISTE/usage",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_usage_sem_resgates(client, db_session) -> None:
    """Cupom sem resgates retorna lista vazia."""
    coupon = Coupon(
        code="VAZIO10",
        discount_type=DiscountType.PERCENT,
        value=10.0,
        active=True,
    )
    db_session.add(coupon)
    await db_session.commit()
    token = await _staff_token(client, db_session, "dom28_s2@x.com")
    resp = await client.get(
        "/api/v1/admin/coupons/VAZIO10/usage",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_usage_com_resgates(client, db_session) -> None:
    """Retorna resgates com order_reference e buyer_email."""
    coupon = Coupon(
        code="USADO10",
        discount_type=DiscountType.FIXED,
        value=10.0,
        active=True,
    )
    db_session.add(coupon)
    await db_session.flush()
    order = Order(
        buyer_email="buyer@x.com",
        amount=Decimal("90.00"),
        status=OrderStatus.PAID,
    )
    db_session.add(order)
    await db_session.flush()
    db_session.add(
        CouponRedemption(coupon_id=coupon.id, order_id=order.id)
    )
    await db_session.commit()
    token = await _staff_token(client, db_session, "dom28_s3@x.com")
    resp = await client.get(
        "/api/v1/admin/coupons/USADO10/usage",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["order_reference"] == order.reference
    assert items[0]["buyer_email"] == "buyer@x.com"
