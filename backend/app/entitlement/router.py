"""Rotas de 'Minha Biblioteca': listar posses e reemitir link de download."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.catalog.schemas import ProductListItem
from app.core.clock import Clock
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.delivery.services import DownloadIssuer
from app.entitlement.services import EntitlementService, NotOwned
from app.security.deps import get_current_user
from app.security.tokens import TokenFactory

router = APIRouter(prefix="/api/v1/library", tags=["library"])


def get_entitlements(
    session: AsyncSession = Depends(get_session),
) -> EntitlementService:
    """Monta o serviço de posse com a sessão injetada."""
    return EntitlementService(session)


@router.get("", response_model=list[ProductListItem])
async def my_library(
    user: User = Depends(get_current_user),
    entitlements: EntitlementService = Depends(get_entitlements),
):
    """Lista os e-books que o usuário autenticado possui."""
    return await entitlements.library(user.id)


@router.post("/{slug}/download-link")
async def reissue_download_link(
    slug: str,
    user: User = Depends(get_current_user),
    entitlements: EntitlementService = Depends(get_entitlements),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    """Reemite um link de download para um e-book possuído pelo usuário."""
    issuer = DownloadIssuer(
        session,
        TokenFactory(),
        Clock(),
        settings.download_ttl_days,
        settings.download_max,
    )
    try:
        grant = await entitlements.reissue_download(user.id, slug, issuer)
    except NotOwned as error:
        raise HTTPException(
            status_code=403, detail="Você não possui este e-book"
        ) from error
    return {"token": grant.token, "url": f"/api/v1/download/{grant.token}"}
