"""Serviço de cupons: validação, cálculo de desconto e resgate (async)."""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import Clock
from app.coupons.models import Coupon, CouponRedemption, DiscountType
from app.orders.models import Order

_logger = logging.getLogger(__name__)


class CouponInvalid(Exception):
    """Levantada quando o cupom é inválido, inativo, expirado ou esgotado."""


class CouponCodeAlreadyExists(Exception):
    """Levantada ao tentar criar um cupom com código já existente."""


class CouponAdminService:
    """Cria e gerencia cupons para o painel administrativo."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def create(
        self,
        code: str,
        discount_type: str,
        value: Decimal,
        max_redemptions: int | None = None,
        valid_until: datetime | None = None,
    ) -> Coupon:
        """Cria um cupom ativo; levanta CouponCodeAlreadyExists se o código existir."""
        existing = await self.session.scalars(
            select(Coupon).where(Coupon.code == code.upper())
        )
        if existing.first() is not None:
            raise CouponCodeAlreadyExists(code)
        try:
            dtype = DiscountType(discount_type)
        except ValueError as err:
            raise ValueError(f"discount_type inválido: {discount_type!r}") from err
        coupon = Coupon(
            code=code.upper(),
            discount_type=dtype,
            value=float(value),
            active=True,
            max_redemptions=max_redemptions,
            valid_until=valid_until,
        )
        self.session.add(coupon)
        await self.session.flush()
        return coupon


class CouponService:
    """Valida cupons e aplica descontos a pedidos (idempotente por pedido)."""

    def __init__(self, session: AsyncSession, clock: Clock) -> None:
        """Recebe a sessão e o relógio por injeção."""
        self.session = session
        self.clock = clock

    async def compute_total(self, code: str, amount: Decimal) -> Decimal:
        """Retorna o total com desconto; levanta CouponInvalid se inválido."""
        coupon = await self._require_valid(code)
        return self._apply_discount(coupon, amount)

    async def apply_to_order(self, code: str, order: Order) -> None:
        """Valida o cupom, aplica o desconto ao pedido e registra o resgate.

        Desativa automaticamente o cupom quando o limite de resgates é atingido.
        """
        coupon = await self._require_valid(code)
        order.amount = self._apply_discount(coupon, Decimal(str(order.amount)))
        self.session.add(CouponRedemption(coupon_id=coupon.id, order_id=order.id))
        coupon.redemptions_count = coupon.redemptions_count + 1
        if (
            coupon.max_redemptions is not None
            and coupon.redemptions_count >= coupon.max_redemptions
        ):
            coupon.active = False
            _logger.info(
                "domain_event",
                extra={
                    "event": "coupon_auto_deactivated",
                    "coupon_code": coupon.code,
                    "redemptions_count": coupon.redemptions_count,
                    "max_redemptions": coupon.max_redemptions,
                },
            )
        await self.session.flush()

    async def _require_valid(self, code: str) -> Coupon:
        """Busca o cupom (sem espaços, maiúsculo) e valida ativo/validade/limite."""
        result = await self.session.scalars(
            select(Coupon).where(Coupon.code == code.strip().upper())
        )
        coupon = result.first()
        if coupon is None or not coupon.active:
            raise CouponInvalid("cupom inválido")
        if coupon.valid_until is not None and self.clock.now() >= coupon.valid_until:
            raise CouponInvalid("cupom expirado")
        if (
            coupon.max_redemptions is not None
            and coupon.redemptions_count >= coupon.max_redemptions
        ):
            raise CouponInvalid("cupom esgotado")
        return coupon

    def _apply_discount(self, coupon: Coupon, amount: Decimal) -> Decimal:
        """Calcula o total com desconto, nunca negativo."""
        value = Decimal(str(coupon.value))
        if coupon.discount_type == DiscountType.PERCENT:
            discount = (amount * value) / Decimal("100")
        else:
            discount = value
        total = amount - discount
        if total < 0:
            return Decimal("0.00")
        return total.quantize(Decimal("0.01"))
