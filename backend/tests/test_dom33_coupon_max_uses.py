"""Testes DOM-33: expiração automática de cupom ao atingir max_redemptions."""

from __future__ import annotations

from decimal import Decimal

from app.core.clock import Clock
from app.coupons.models import Coupon, DiscountType
from app.coupons.services import CouponService
from app.orders.models import Order, OrderStatus


async def _make_coupon(db_session, code: str, max_redemptions: int | None) -> Coupon:
    """Cria cupom de 10% com limite opcional de resgates."""
    coupon = Coupon(
        code=code,
        discount_type=DiscountType.PERCENT,
        value=10.0,
        active=True,
        max_redemptions=max_redemptions,
        redemptions_count=0,
    )
    db_session.add(coupon)
    await db_session.flush()
    return coupon


async def _make_order(db_session, amount: str = "100.00") -> Order:
    """Cria pedido pendente para aplicar cupom."""
    order = Order(
        buyer_email="buyer@dom33.com",
        amount=Decimal(amount),
        status=OrderStatus.PENDING,
    )
    db_session.add(order)
    await db_session.flush()
    return order


async def test_cupom_desativa_ao_atingir_limite_1(db_session) -> None:
    """Cupom com max_redemptions=1 deve ficar inativo após 1 resgate."""
    coupon = await _make_coupon(db_session, "DOM33A", 1)
    order = await _make_order(db_session)
    service = CouponService(db_session, Clock())
    await service.apply_to_order("DOM33A", order)
    await db_session.commit()
    assert coupon.active is False


async def test_cupom_permanece_ativo_antes_do_limite(db_session) -> None:
    """Cupom com max_redemptions=2 deve continuar ativo após apenas 1 resgate."""
    coupon = await _make_coupon(db_session, "DOM33B", 2)
    order = await _make_order(db_session)
    service = CouponService(db_session, Clock())
    await service.apply_to_order("DOM33B", order)
    await db_session.commit()
    assert coupon.active is True


async def test_cupom_sem_limite_nunca_desativa(db_session) -> None:
    """Cupom sem max_redemptions nunca é desativado automaticamente."""
    coupon = await _make_coupon(db_session, "DOM33C", None)
    for i in range(3):
        order = await _make_order(db_session, f"{(i + 1) * 100:.2f}")
        await CouponService(db_session, Clock()).apply_to_order("DOM33C", order)
    await db_session.commit()
    assert coupon.active is True
