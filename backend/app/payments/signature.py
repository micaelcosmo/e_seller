"""Validação de assinatura do webhook Mercado Pago (HMAC-SHA256).

Referência: https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks
Fluxo:
  1. Header `x-signature` contém `ts=<epoch>,v1=<hmac-hex>`.
  2. Header `x-request-id` é o ID único da requisição.
  3. Mensagem assinada: `id:<payment_id>;request-id:<request-id>;ts:<epoch>`.
  4. Chave: MERCADOPAGO_WEBHOOK_SECRET (Settings).
"""

from __future__ import annotations

import hashlib
import hmac


class InvalidWebhookSignature(Exception):
    """Levantada quando a assinatura do webhook é inválida ou ausente."""


class WebhookSignatureValidator:
    """Valida a assinatura HMAC-SHA256 enviada pelo Mercado Pago no header."""

    def __init__(self, secret: str) -> None:
        """Recebe o segredo do webhook (Settings.mercadopago_webhook_secret)."""
        self.secret = secret

    def validate(
        self,
        payment_id: str,
        request_id: str,
        x_signature: str,
    ) -> None:
        """Valida o header x-signature; levanta InvalidWebhookSignature se inválido.

        Extrai `ts` e `v1` do header, reconstrói a mensagem assinada e compara
        com HMAC calculado. Levanta InvalidWebhookSignature em qualquer falha.
        """
        ts = self._extract_field(x_signature, "ts")
        signature = self._extract_field(x_signature, "v1")
        message = f"id:{payment_id};request-id:{request_id};ts:{ts}"
        expected = hmac.new(
            self.secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise InvalidWebhookSignature("assinatura inválida")

    def _extract_field(self, header: str, field: str) -> str:
        """Extrai o valor de um campo do header x-signature (key=value,...)."""
        for part in header.split(","):
            part = part.strip()
            if part.startswith(f"{field}="):
                return part[len(f"{field}="):]
        raise InvalidWebhookSignature(f"campo '{field}' ausente no x-signature")
