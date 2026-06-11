"""Rotas do perfil fiscal do usuário autenticado (billing_profile)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.billing.schemas import BillingProfileIn, BillingProfileOut
from app.billing.services import BillingService
from app.core.db import get_session
from app.security.deps import get_current_user

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


def get_billing_service(
    session: AsyncSession = Depends(get_session),
) -> BillingService:
    """Constrói o serviço de faturamento com a sessão injetada."""
    return BillingService(session)


@router.get("/profile", response_model=BillingProfileOut)
async def read_profile(
    user: User = Depends(get_current_user),
    billing: BillingService = Depends(get_billing_service),
) -> object:
    """Retorna o perfil fiscal do usuário autenticado (404 se não existir)."""
    profile = await billing.get_profile(user.id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Perfil fiscal não cadastrado")
    return profile


@router.put("/profile", response_model=BillingProfileOut)
async def save_profile(
    data: BillingProfileIn,
    user: User = Depends(get_current_user),
    billing: BillingService = Depends(get_billing_service),
) -> object:
    """Cria ou atualiza o perfil fiscal do usuário autenticado.

    Levanta InvalidDocument (422) via handler global de exceções de domínio.
    """
    return await billing.upsert_profile(
        user.id,
        person_type=data.person_type,
        legal_name=data.legal_name,
        document=data.document,
        address_line=data.address_line,
        city=data.city,
        state=data.state,
        postal_code=data.postal_code,
        country=data.country,
    )
