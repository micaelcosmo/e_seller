"""Rota pública de validação de cupom (preview de desconto no checkout)."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import Clock
from app.core.db import get_session
from app.coupons.services import CouponInvalid, CouponService

router = APIRouter(prefix="/api/v1/coupons", tags=["coupons"])


class ValidateIn(BaseModel):
    """Entrada: código do cupom e valor a descontar."""

    code: str
    amount: Decimal


class ValidateOut(BaseModel):
    """Saída: total com desconto e o valor descontado."""

    valid: bool
    total: Decimal
    discount: Decimal


def get_coupon_service(
    session: AsyncSession = Depends(get_session),
) -> CouponService:
    """Monta o serviço de cupom com a sessão e o relógio."""
    return CouponService(session, Clock())


@router.post("/validate", response_model=ValidateOut)
async def validate(
    data: ValidateIn,
    coupons: CouponService = Depends(get_coupon_service),
):
    """Valida o cupom e retorna o total com desconto (preview)."""
    try:
        total = await coupons.compute_total(data.code, data.amount)
    except CouponInvalid as error:
        raise HTTPException(status_code=422, detail="Cupom inválido") from error
    return ValidateOut(valid=True, total=total, discount=data.amount - total)
