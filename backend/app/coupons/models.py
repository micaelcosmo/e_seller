"""Models de cupons: Coupon e CouponRedemption."""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DiscountType(enum.StrEnum):
    """Tipo de desconto do cupom."""

    PERCENT = "percent"
    FIXED = "fixed"


class Coupon(Base):
    """Cupom de desconto aplicável no checkout."""

    __tablename__ = "coupon"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    discount_type: Mapped[DiscountType] = mapped_column(Enum(DiscountType))
    value: Mapped[float] = mapped_column(Numeric(10, 2))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    max_redemptions: Mapped[int | None] = mapped_column(nullable=True)
    redemptions_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CouponRedemption(Base):
    """Registro de uso de um cupom em um pedido (1 por pedido)."""

    __tablename__ = "coupon_redemption"

    id: Mapped[int] = mapped_column(primary_key=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupon.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
