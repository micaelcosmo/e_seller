"""Rotas públicas da newsletter: inscrever e cancelar."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import Clock
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.core.email import EmailService
from app.newsletter.services import NewsletterService

router = APIRouter(prefix="/api/v1/newsletter", tags=["newsletter"])


class SubscribeIn(BaseModel):
    """Entrada com o e-mail do inscrito."""

    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Valida de forma simples o formato do e-mail."""
        candidate = value.strip()
        if "@" not in candidate or "." not in candidate.split("@")[-1]:
            raise ValueError("E-mail inválido")
        return candidate


def get_newsletter_service(
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> NewsletterService:
    """Monta o serviço de newsletter com a sessão, relógio e serviço de e-mail."""
    return NewsletterService(session, Clock(), EmailService(settings))


@router.post("/subscribe", status_code=202)
async def subscribe(
    data: SubscribeIn,
    newsletter: NewsletterService = Depends(get_newsletter_service),
):
    """Inscreve um e-mail na newsletter."""
    await newsletter.subscribe(data.email)
    return {"status": "subscribed"}


@router.post("/unsubscribe", status_code=202)
async def unsubscribe(
    data: SubscribeIn,
    newsletter: NewsletterService = Depends(get_newsletter_service),
):
    """Cancela a inscrição de um e-mail."""
    await newsletter.unsubscribe(data.email)
    return {"status": "unsubscribed"}
