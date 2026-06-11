"""Schemas (Pydantic) de entrada/saída para estornos (refunds)."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.refunds.models import RefundStatus


class RefundIn(BaseModel):
    """Dados de entrada do estorno: referência do pedido, valor opcional e motivo."""

    order_reference: str
    amount: Decimal | None = None
    reason: str = ""


class RefundOut(BaseModel):
    """Representação de saída de um estorno."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    payment_id: int
    amount: Decimal
    reason: str
    status: RefundStatus
