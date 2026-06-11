"""Audit log de ações administrativas: modelo e serviço de gravação."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AdminAuditLog(Base):
    """Registro imutável de ações de escrita no painel administrativo."""

    __tablename__ = "admin_audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_email: Mapped[str] = mapped_column(String(254), index=True)
    action: Mapped[str] = mapped_column(String(80))
    resource_type: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str] = mapped_column(String(120), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class AdminAuditService:
    """Grava entradas no audit log de ações administrativas."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção de dependência."""
        self.session = session

    async def log(
        self,
        actor_email: str,
        action: str,
        resource_type: str,
        resource_id: str = "",
        detail: str = "",
    ) -> AdminAuditLog:
        """Insere uma entrada no audit log e faz flush (sem commit).

        O commit é responsabilidade da transação externa.
        """
        entry = AdminAuditLog(
            actor_email=actor_email,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            detail=detail,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry
