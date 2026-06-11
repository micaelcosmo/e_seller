"""Models de pedidos: Order e OrderItem."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def generate_reference() -> str:
    """Gera uma referência pública única (UUID) para o pedido."""
    return str(uuid.uuid4())


class OrderStatus(enum.StrEnum):
    """Estados possíveis de um pedido."""

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base):
    """Pedido de compra (multi-item; no MVP, 1 item)."""

    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=generate_reference
    )
    buyer_email: Mapped[str] = mapped_column(String(254), index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id"), nullable=True, index=True
    )
    billing_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("billing_profile.id"), nullable=True, index=True
    )
    # Numeric(10,2) → Decimal; evita erro de arredondamento em aritmética monetária.
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Auditoria: registra quando o pedido foi alterado pela última vez.
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )


class OrderItem(Base):
    """Item de um pedido, com o preço congelado no momento da compra."""

    __tablename__ = "order_item"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_order_item_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    # Numeric(10,2) → Decimal; preço é congelado no momento da compra.
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantity: Mapped[int] = mapped_column(default=1)
    order: Mapped[Order] = relationship(back_populates="items")
