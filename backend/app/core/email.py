"""Serviço de e-mail transacional (SMTP) para notificações de compra."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import Settings

_logger = logging.getLogger(__name__)


class EmailFailCounter:
    """Contador thread-safe simples de falhas de envio de e-mail (in-memory).

    Armazenado em app.state para que os alertas possam monitorar falhas
    sem acessar o banco de dados.
    """

    def __init__(self) -> None:
        """Inicializa o contador zerado."""
        self._count: int = 0

    def increment(self) -> None:
        """Incrementa o contador de falhas."""
        self._count += 1

    @property
    def count(self) -> int:
        """Retorna o total de falhas acumuladas desde o início da aplicação."""
        return self._count


class EmailService:
    """Envia e-mails transacionais via SMTP.

    Não levanta exceção em caso de falha — apenas loga o erro para não
    bloquear o fluxo de negócio (webhook ainda retorna 200).
    """

    def __init__(
        self,
        settings: Settings,
        counter: EmailFailCounter | None = None,
    ) -> None:
        """Recebe as configurações SMTP e contador de falhas por injeção."""
        self.settings = settings
        self._counter = counter

    def _enabled(self) -> bool:
        """Retorna True se o SMTP está configurado via env."""
        return bool(self.settings.smtp_host)

    def send_purchase_confirmation(
        self, buyer_email: str, product_title: str, order_reference: str
    ) -> None:
        """Envia confirmação de compra ao comprador.

        Falha silenciosa: loga o erro mas nunca propaga a exceção.
        """
        if not self._enabled():
            return
        msg = EmailMessage()
        msg["Subject"] = f"Compra confirmada: {product_title}"
        msg["From"] = self.settings.smtp_from
        msg["To"] = buyer_email
        msg.set_content(
            f"Olá!\n\n"
            f"Sua compra de '{product_title}' foi confirmada.\n"
            f"Referência do pedido: {order_reference}\n\n"
            f"Acesse sua biblioteca para baixar o e-book.\n\n"
            f"Obrigado pela compra!"
        )
        try:
            with smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port, timeout=10
            ) as server:
                server.starttls()
                if self.settings.smtp_user:
                    server.login(self.settings.smtp_user, self.settings.smtp_password)
                server.send_message(msg)
        except Exception as exc:
            _logger.warning(
                "Falha ao enviar e-mail de confirmação para %s: %s",
                buyer_email,
                exc,
            )
            if self._counter is not None:
                self._counter.increment()

    def send_newsletter_welcome(self, email: str) -> None:
        """Envia e-mail de boas-vindas ao inscrito na newsletter.

        Falha silenciosa: loga o erro mas nunca propaga a exceção.
        """
        if not self._enabled():
            return
        msg = EmailMessage()
        msg["Subject"] = "Bem-vindo(a) à newsletter — e_seller"
        msg["From"] = self.settings.smtp_from
        msg["To"] = email
        msg.set_content(
            "Olá!\n\nObrigado por se inscrever na nossa newsletter.\n"
            "Você receberá novidades sobre lançamentos e promoções de e-books.\n\n"
            "Para cancelar sua inscrição a qualquer momento, acesse nosso site."
        )
        try:
            with smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port, timeout=10
            ) as server:
                server.starttls()
                if self.settings.smtp_user:
                    server.login(self.settings.smtp_user, self.settings.smtp_password)
                server.send_message(msg)
        except Exception as exc:
            _logger.warning(
                "Falha ao enviar e-mail de boas-vindas para %s: %s",
                email,
                exc,
            )
            if self._counter is not None:
                self._counter.increment()

    def send_download_expiring(
        self, email: str, product_title: str, expires_at: str
    ) -> None:
        """Avisa o usuário que um link de download vai expirar em breve.

        Falha silenciosa: loga o erro mas nunca propaga a exceção.
        """
        if not self._enabled():
            return
        msg = EmailMessage()
        msg["Subject"] = f"Download expirando em breve: {product_title}"
        msg["From"] = self.settings.smtp_from
        msg["To"] = email
        msg.set_content(
            f"Olá!\n\nSeu link de download de '{product_title}' expira em "
            f"{expires_at}.\n\nAcesse sua biblioteca para baixar antes que expire.\n\n"
            f"Obrigado por comprar na e_seller!"
        )
        try:
            with smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port, timeout=10
            ) as server:
                server.starttls()
                if self.settings.smtp_user:
                    server.login(self.settings.smtp_user, self.settings.smtp_password)
                server.send_message(msg)
        except Exception as exc:
            _logger.warning(
                "Falha ao enviar aviso de expiração para %s: %s",
                email,
                exc,
            )
            if self._counter is not None:
                self._counter.increment()

    def send_password_reset(self, email: str, reset_link: str) -> None:
        """Envia link de redefinição de senha ao usuário.

        Falha silenciosa: loga o erro mas nunca propaga a exceção.
        """
        if not self._enabled():
            return
        msg = EmailMessage()
        msg["Subject"] = "Redefinição de senha — e_seller"
        msg["From"] = self.settings.smtp_from
        msg["To"] = email
        msg.set_content(
            f"Olá!\n\nClique no link abaixo para redefinir sua senha "
            f"(válido por 1 hora):\n{reset_link}\n\n"
            f"Se você não solicitou a redefinição, ignore este e-mail."
        )
        try:
            with smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port, timeout=10
            ) as server:
                server.starttls()
                if self.settings.smtp_user:
                    server.login(self.settings.smtp_user, self.settings.smtp_password)
                server.send_message(msg)
        except Exception as exc:
            _logger.warning(
                "Falha ao enviar e-mail de redefinição para %s: %s",
                email,
                exc,
            )
            if self._counter is not None:
                self._counter.increment()
