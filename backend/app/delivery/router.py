"""Rotas de entrega: download protegido por token (grant)."""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import Clock
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.core.rate_limit import RateLimit
from app.delivery.models import DownloadLog
from app.delivery.services import FileStreamer, GrantValidator
from app.security.storage import ProtectedStorage

router = APIRouter(prefix="/api/v1/download", tags=["delivery"])

# 20 requisições de download por IP por minuto (grant já limita por token).
_download_limit = RateLimit(max_requests=20, window_seconds=60)


def get_grant_validator(session: AsyncSession = Depends(get_session)) -> GrantValidator:
    """Monta o validador de grant com a sessão e o relógio."""
    return GrantValidator(session, Clock())


def get_file_streamer(
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> FileStreamer:
    """Monta o leitor de arquivo com o armazenamento protegido."""
    return FileStreamer(session, ProtectedStorage(settings.storage_dir))


@router.get("/{token}")
async def download(
    token: str,
    request: Request,
    validator: GrantValidator = Depends(get_grant_validator),
    streamer: FileStreamer = Depends(get_file_streamer),
    session: AsyncSession = Depends(get_session),
    _limit: None = Depends(_download_limit),
) -> Response:
    """Valida o token, registra a auditoria e transmite o arquivo do e-book.

    Levanta GrantNotFound (404), GrantExpired (410), DownloadLimitReached (429)
    ou FileMissing (404) via handler global de exceções de domínio.
    """
    from app.accounts.services_aaa import UserActivityLogService

    grant = await validator.consume(token)
    content, file_name = await streamer.read_for_grant(grant)

    # Auditoria do download (anti-pirataria): registra o evento com o IP em hash.
    client_ip = request.client.host if request.client is not None else ""
    ip_hash = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()
    session.add(DownloadLog(download_grant_id=grant.id, ip_hash=ip_hash))

    activity = UserActivityLogService(session)
    await activity.log(
        "download",
        user_id=None,
        grant_id=grant.id,
        product_id=grant.product_id,
    )

    headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}
    return Response(
        content=content, media_type="application/octet-stream", headers=headers
    )
