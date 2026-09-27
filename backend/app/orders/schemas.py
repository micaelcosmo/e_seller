"""Schemas (Pydantic) de pedidos."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.orders.models import OrderStatus


class OrderCreateIn(BaseModel):
    """Dados de entrada para criar um pedido."""

    product_slug: str
    buyer_email: str
    coupon_code: str | None = None

    @field_validator("buyer_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Valida de forma simples o formato do e-mail (sem dependência extra)."""
        candidate = value.strip()
        if "@" not in candidate or "." not in candidate.split("@")[-1]:
            raise ValueError("E-mail inválido")
        return candidate


class OrderOut(BaseModel):
    """Dados de saída de um pedido."""

    model_config = ConfigDict(from_attributes=True)

    reference: str
    status: OrderStatus
    amount: Decimal
    checkout_url: str | None = None


class OrderAdminListItemOut(BaseModel):
    """Item da lista de pedidos do painel: status, valor, data e comprador (US-07)."""

    model_config = ConfigDict(from_attributes=True)

    reference: str
    buyer_email: str
    status: OrderStatus
    amount: Decimal
    created_at: datetime


class OrderItemAdminOut(BaseModel):
    """Dados de um item de pedido para visão administrativa."""

    model_config = ConfigDict(from_attributes=True)

    product_id: int
    unit_price: Decimal
    quantity: int


class OrderAdminDetailOut(BaseModel):
    """Dados completos de um pedido para visão administrativa."""

    model_config = ConfigDict(from_attributes=True)

    reference: str
    buyer_email: str
    status: OrderStatus
    amount: Decimal
    created_at: datetime
    items: list[OrderItemAdminOut]
