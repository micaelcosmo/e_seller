"""Testes BEE: EmailService — comportamento sem SMTP configurado."""

from __future__ import annotations

from app.core.email import EmailFailCounter, EmailService


def _make_service(smtp_host: str = "") -> tuple[EmailService, EmailFailCounter]:
    """Cria um EmailService sem SMTP (smtp_host vazio = modo log-only)."""
    from app.core.config import Settings

    settings = Settings(
        app_env="test",
        database_url="sqlite+aiosqlite:///./test.db",
        smtp_host=smtp_host,
    )
    counter = EmailFailCounter()
    return EmailService(settings, counter), counter


def test_send_purchase_confirmation_sem_smtp_nao_levanta() -> None:
    """EMAIL-001: sem SMTP, send_purchase_confirmation não levanta exceção."""
    service, counter = _make_service()
    service.send_purchase_confirmation("user@test.com", "Python Pro", "REF-001")
    assert counter.count == 0


def test_send_password_reset_sem_smtp_nao_levanta() -> None:
    """EMAIL-002: sem SMTP configurado, send_password_reset não levanta exceção."""
    service, counter = _make_service()
    service.send_password_reset("user@test.com", "https://e-seller.app/reset/abc123")
    assert counter.count == 0


def test_send_download_expiring_sem_smtp_nao_levanta() -> None:
    """EMAIL-003: sem SMTP configurado, send_download_expiring não levanta exceção."""
    service, counter = _make_service()
    service.send_download_expiring("user@test.com", "Python Pro", "2026-06-20 23:59")
    assert counter.count == 0


def test_send_newsletter_welcome_sem_smtp_nao_levanta() -> None:
    """EMAIL-004: sem SMTP configurado, send_newsletter_welcome não levanta exceção."""
    service, counter = _make_service()
    service.send_newsletter_welcome("user@test.com")
    assert counter.count == 0


def test_fail_counter_incrementa_em_falha() -> None:
    """EMAIL-005: EmailFailCounter.increment() acumula corretamente."""
    counter = EmailFailCounter()
    assert counter.count == 0
    counter.increment()
    counter.increment()
    assert counter.count == 2
