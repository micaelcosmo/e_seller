"""Rotas de pagamento: webhook de notificação (idempotente)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import Clock
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.core.email import EmailService
from app.core.rate_limit import RateLimit
from app.delivery.services import DownloadIssuer
from app.entitlement.services import EntitlementService
from app.payments.services import WebhookNotification, WebhookProcessor
from app.payments.signature import InvalidWebhookSignature, WebhookSignatureValidator
from app.payments.status_map import StatusMapper
from app.security.tokens import TokenFactory

router = APIRouter(prefix="/api/v1/webhooks", tags=["payments"])

# 30 notificações por minuto por IP (Mercado Pago pode reenviar).
_webhook_limit = RateLimit(max_requests=30, window_seconds=60)


class WebhookIn(BaseModel):
    """Corpo da notificação de pagamento (modo fake/dev)."""

    provider_payment_id: str
    order_reference: str
    provider_status: str = "approved"


def get_webhook_processor(
    request: Request,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> WebhookProcessor:
    """Monta o WebhookProcessor com mapeador de status e emissor de download."""
    clock = Clock()
    issuer = DownloadIssuer(
        session=session,
        token_factory=TokenFactory(),
        clock=clock,
        ttl_days=settings.download_ttl_days,
        max_downloads=settings.download_max,
    )
    counter = getattr(request.app.state, "email_fail_counter", None)
    return WebhookProcessor(
        session,
        StatusMapper(),
        issuer,
        clock,
        EntitlementService(session),
        EmailService(settings, counter),
    )


@router.post("/mercadopago")
async def mercadopago_webhook(
    data: WebhookIn,
    processor: WebhookProcessor = Depends(get_webhook_processor),
    settings: Settings = Depends(get_settings),
    _limit: None = Depends(_webhook_limit),
    x_signature: str | None = Header(default=None),
    x_request_id: str | None = Header(default=None),
):
    """Recebe a notificação e a aplica de forma idempotente.

    Quando payment_provider=mercadopago, valida a assinatura HMAC-SHA256
    do header x-signature antes de processar (RNF-02).
    """
    if settings.payment_provider == "mercadopago":
        if not x_signature or not x_request_id:
            raise HTTPException(
                status_code=400,
                detail="Headers x-signature e x-request-id são obrigatórios.",
            )
        validator = WebhookSignatureValidator(settings.mercadopago_webhook_secret)
        try:
            validator.validate(
                payment_id=data.provider_payment_id,
                request_id=x_request_id,
                x_signature=x_signature,
            )
        except InvalidWebhookSignature as error:
            raise HTTPException(
                status_code=401, detail="Assinatura inválida"
            ) from error

    notification = WebhookNotification(
        provider_payment_id=data.provider_payment_id,
        order_reference=data.order_reference,
        provider_status=data.provider_status,
    )
    result = await processor.process(notification)
    return {"outcome": result.outcome, "order_reference": result.order_reference}
