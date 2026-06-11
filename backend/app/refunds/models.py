"""Model de estorno: Refund (parcial ou total) vinculado a um pagamento."""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class RefundStatus(enum.StrEnum):
    """Estado do estorno no provedor (simulado no MVP)."""

    REQUESTED = "requested"
    COMPLETED = "completed"
    FAILED = "failed"


class Refund(Base):
    """Estorno de um pagamento (parcial ou total), com motivo e estado."""

    __tablename__ = "refund"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payment.id"), index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), index=True)
    # Numeric(10,2) → Decimal; valor monetário do estorno.
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    reason: Mapped[str] = mapped_column(String(280), default="")
    status: Mapped[RefundStatus] = mapped_column(
        Enum(RefundStatus), default=RefundStatus.REQUESTED
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
