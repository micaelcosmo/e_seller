"""Testes BEQ-28: estatísticas de uso por cupom."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.core.config import get_settings
from app.coupons.models import Coupon, CouponRedemption, DiscountType
from app.security.jwt import JwtService
from app.security.passwords import PasswordHasher


async def _admin_token(db_session) -> str:
    """Cria usuário admin e retorna seu JWT."""
    settings = get_settings()
    hasher = PasswordHasher(settings.password_hash_iterations)
    user = User(
        email="admin_beq28@test.com",
        password_hash=hasher.hash("x"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return JwtService(secret_key=settings.app_secret_key).issue(user.email)


async def test_stats_cupom_sem_uso(client, db_session) -> None:
    """GET /admin/coupons/{code}/stats retorna total_uses=0 e last_used_at=null."""
    token = await _admin_token(db_session)
    coupon = Coupon(
        code="NOUSE28",
        discount_type=DiscountType.FIXED,
        value=10.0,
        active=True,
    )
    db_session.add(coupon)
    await db_session.commit()
    resp = await client.get(
        f"/api/v1/admin/coupons/{coupon.code}/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_uses"] == 0
    assert data["last_used_at"] is None


async def test_stats_cupom_inexistente_retorna_404(client, db_session) -> None:
    """GET /admin/coupons/NAOEXI/stats retorna 404."""
    token = await _admin_token(db_session)
    resp = await client.get(
        "/api/v1/admin/coupons/NAOEXI/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_stats_com_resgates(client, db_session) -> None:
    """GET /admin/coupons/{code}/stats retorna total_uses correto com resgates."""
    from decimal import Decimal

    from app.orders.models import Order, OrderStatus

    token = await _admin_token(db_session)
    coupon = Coupon(
        code="USED28",
        discount_type=DiscountType.PERCENT,
        value=10.0,
        active=True,
        redemptions_count=2,
    )
    db_session.add(coupon)
    order = Order(
        buyer_email="x@test.com",
        amount=Decimal("9.90"),
        status=OrderStatus.PAID,
    )
    db_session.add(order)
    await db_session.commit()
    redemption = CouponRedemption(coupon_id=coupon.id, order_id=order.id)
    db_session.add(redemption)
    await db_session.commit()
    resp = await client.get(
        f"/api/v1/admin/coupons/{coupon.code}/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_uses"] == 1
    assert data["last_used_at"] is not None
