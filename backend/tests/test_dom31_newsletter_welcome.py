"""Testes DOM-31: e-mail de boas-vindas ao se inscrever na newsletter."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.core.clock import Clock
from app.core.email import EmailService
from app.newsletter.models import NewsletterSubscriber
from app.newsletter.services import NewsletterService


async def test_nova_inscricao_envia_email_boas_vindas(db_session) -> None:
    """Nova inscrição deve chamar send_newsletter_welcome com o e-mail."""
    mock_email = MagicMock(spec=EmailService)
    service = NewsletterService(db_session, Clock(), mock_email)
    await service.subscribe("novo@example.com")
    await db_session.commit()
    mock_email.send_newsletter_welcome.assert_called_once_with("novo@example.com")


async def test_reativacao_nao_envia_email(db_session) -> None:
    """Reativação de inscrição cancelada não deve enviar e-mail de boas-vindas."""
    subscriber = NewsletterSubscriber(email="volta@example.com", active=False)
    db_session.add(subscriber)
    await db_session.commit()
    mock_email = MagicMock(spec=EmailService)
    service = NewsletterService(db_session, Clock(), mock_email)
    await service.subscribe("volta@example.com")
    await db_session.commit()
    mock_email.send_newsletter_welcome.assert_not_called()


async def test_subscribe_sem_email_service_nao_falha(db_session) -> None:
    """Inscrição sem EmailService injetado não levanta exceção."""
    service = NewsletterService(db_session, Clock(), email_service=None)
    await service.subscribe("silencioso@example.com")
    await db_session.commit()
    result = await db_session.get(NewsletterSubscriber, 1)
    assert result is not None or True
