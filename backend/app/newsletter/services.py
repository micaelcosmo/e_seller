"""Serviço de newsletter: inscrever e cancelar (async, idempotente)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import Clock
from app.core.email import EmailService
from app.newsletter.models import NewsletterSubscriber


class NewsletterService:
    """Gerencia inscrições da newsletter com envio de e-mail de boas-vindas."""

    def __init__(
        self,
        session: AsyncSession,
        clock: Clock,
        email_service: EmailService | None = None,
    ) -> None:
        """Recebe a sessão, o relógio e o serviço de e-mail por injeção."""
        self.session = session
        self.clock = clock
        self.email_service = email_service

    async def subscribe(self, email: str) -> None:
        """Inscreve o e-mail (idempotente); reativa se estava cancelado.

        Envia e-mail de boas-vindas apenas para novas inscrições (não reativações).
        """
        subscriber = await self._by_email(email)
        is_new = subscriber is None
        if is_new:
            self.session.add(NewsletterSubscriber(email=email, active=True))
        else:
            subscriber.active = True
            subscriber.unsubscribed_at = None
        await self.session.flush()
        if is_new and self.email_service is not None:
            self.email_service.send_newsletter_welcome(email)

    async def unsubscribe(self, email: str) -> None:
        """Cancela a inscrição (registra a data do opt-out)."""
        subscriber = await self._by_email(email)
        if subscriber is not None:
            subscriber.active = False
            subscriber.unsubscribed_at = self.clock.now()
            await self.session.flush()

    async def _by_email(self, email: str) -> NewsletterSubscriber | None:
        """Busca um inscrito pelo e-mail (ou None)."""
        result = await self.session.scalars(
            select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
        )
        return result.first()


class NewsletterAdminLister:
    """Lista e conta inscritos da newsletter para o painel administrativo."""

    _PAGE_SIZE_MAX = 100

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    def _base_statement(self, active: bool | None) -> object:
        """Constrói statement base com filtro opcional de status ativo."""
        stmt = select(NewsletterSubscriber)
        if active is not None:
            stmt = stmt.where(NewsletterSubscriber.active == active)
        return stmt

    async def list_subscribers(
        self,
        page: int,
        page_size: int,
        active: bool | None = None,
    ) -> list[NewsletterSubscriber]:
        """Retorna página de inscritos (mais recentes primeiro)."""
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = self._base_statement(active)
        stmt = (
            stmt.order_by(NewsletterSubscriber.id.desc())
            .offset((page - 1) * effective_size)
            .limit(effective_size)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def count_subscribers(self, active: bool | None = None) -> int:
        """Retorna o total de inscritos com os filtros aplicados."""
        from sqlalchemy import func as sa_func

        base = self._base_statement(active)
        count_stmt = select(sa_func.count()).select_from(base.subquery())
        result = await self.session.scalar(count_stmt)
        return int(result or 0)

    async def get_stats(self) -> dict:
        """Retorna estatísticas agregadas da newsletter.

        Campos: total_subscribers, active, inactive, new_last_30_days.
        """
        from sqlalchemy import func as sa_func

        total = await self.count_subscribers()
        active_count = await self.count_subscribers(active=True)
        inactive_count = await self.count_subscribers(active=False)

        cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=30)
        new_stmt = (
            select(sa_func.count())
            .select_from(NewsletterSubscriber)
            .where(
                NewsletterSubscriber.active == True,  # noqa: E712
                NewsletterSubscriber.created_at >= cutoff,
            )
        )
        new_count = int((await self.session.scalar(new_stmt)) or 0)
        return {
            "total_subscribers": total,
            "active": active_count,
            "inactive": inactive_count,
            "new_last_30_days": new_count,
        }
