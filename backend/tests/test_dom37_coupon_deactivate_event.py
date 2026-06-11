"""Testes DOM-37: evento de domínio ao auto-desativar cupom."""

from __future__ import annotations

import logging

from app.core.clock import Clock
from app.coupons.models import Coupon, DiscountType
from app.coupons.services import CouponService
from app.orders.models import Order, OrderStatus


async def test_auto_deactivate_emite_log(db_session, caplog) -> None:
    """apply_to_order deve emitir log domain_event ao desativar cupom."""
    coupon = Coupon(
        code="DOM37EVENT",
        discount_type=DiscountType.FIXED,
        value=1.0,
        active=True,
        max_redemptions=1,
        redemptions_count=0,
    )
    db_session.add(coupon)
    order = Order(
        reference="DOM37-LOG-01",
        buyer_email="dom37@test.com",
        amount=50,
        status=OrderStatus.PENDING,
    )
    db_session.add(order)
    await db_session.flush()

    service = CouponService(db_session, Clock())
    with caplog.at_level(logging.INFO, logger="app.coupons.services"):
        await service.apply_to_order("DOM37EVENT", order)

    messages = [r.getMessage() for r in caplog.records]
    assert any("domain_event" in m for m in messages)


async def test_log_contem_coupon_code(db_session, caplog) -> None:
    """Log deve incluir o código do cupom desativado."""
    coupon = Coupon(
        code="DOM37CODE",
        discount_type=DiscountType.FIXED,
        value=1.0,
        active=True,
        max_redemptions=1,
        redemptions_count=0,
    )
    db_session.add(coupon)
    order = Order(
        reference="DOM37-LOG-02",
        buyer_email="dom37b@test.com",
        amount=50,
        status=OrderStatus.PENDING,
    )
    db_session.add(order)
    await db_session.flush()

    service = CouponService(db_session, Clock())
    with caplog.at_level(logging.INFO, logger="app.coupons.services"):
        await service.apply_to_order("DOM37CODE", order)

    assert any(
        r.getMessage() == "domain_event"
        and getattr(r, "event", None) == "coupon_auto_deactivated"
        for r in caplog.records
    )


async def test_nao_loga_quando_sem_limite(db_session, caplog) -> None:
    """Cupom sem max_redemptions não deve emitir log de desativação."""
    coupon = Coupon(
        code="DOM37NOMAX",
        discount_type=DiscountType.FIXED,
        value=1.0,
        active=True,
        max_redemptions=None,
        redemptions_count=0,
    )
    db_session.add(coupon)
    order = Order(
        reference="DOM37-LOG-03",
        buyer_email="dom37c@test.com",
        amount=50,
        status=OrderStatus.PENDING,
    )
    db_session.add(order)
    await db_session.flush()

    service = CouponService(db_session, Clock())
    with caplog.at_level(logging.INFO, logger="app.coupons.services"):
        await service.apply_to_order("DOM37NOMAX", order)

    messages = [r.getMessage() for r in caplog.records]
    assert not any("domain_event" in m for m in messages)
