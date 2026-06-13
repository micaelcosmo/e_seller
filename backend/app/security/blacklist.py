"""Serviço de blacklist de tokens JWT revogados."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import RevokedToken


class TokenBlacklistService:
    """Gerencia tokens JWT revogados (logout + segurança).

    Tokens são identificados pelo claim `jti` (JWT ID, UUID4).
    Após logout, o jti é inserido na tabela `revoked_token`.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão assíncrona do banco."""
        self.session = session

    async def revoke(self, jti: str, expires_at: datetime) -> None:
        """Persiste o jti como revogado até a expiração original do token."""
        entry = RevokedToken(jti=jti, expires_at=expires_at)
        self.session.add(entry)
        await self.session.commit()

    async def is_revoked(self, jti: str) -> bool:
        """Retorna True se o jti estiver na blacklist (ainda não expirado)."""
        now = datetime.now(tz=UTC)
        result = await self.session.scalars(
            select(RevokedToken).where(
                RevokedToken.jti == jti,
                RevokedToken.expires_at > now,
            )
        )
        return result.first() is not None
