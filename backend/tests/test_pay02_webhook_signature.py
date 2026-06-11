"""Testes de PAY-02: validação de assinatura do webhook Mercado Pago.

Testa a classe WebhookSignatureValidator de forma isolada (sem DB/HTTP).
"""

from __future__ import annotations

import hashlib
import hmac

import pytest

from app.payments.signature import InvalidWebhookSignature, WebhookSignatureValidator


def _make_signature(secret: str, payment_id: str, request_id: str, ts: str) -> str:
    """Gera um x-signature válido para os parâmetros fornecidos."""
    message = f"id:{payment_id};request-id:{request_id};ts:{ts}"
    hmac_hex = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"ts={ts},v1={hmac_hex}"


def test_assinatura_valida_passa():
    """Assinatura correta não levanta InvalidWebhookSignature."""
    secret = "meu-segredo"
    sig = _make_signature(secret, "pay-123", "req-abc", "1717000000")
    validator = WebhookSignatureValidator(secret)
    validator.validate("pay-123", "req-abc", sig)


def test_assinatura_incorreta_falha():
    """Assinatura com HMAC errado levanta InvalidWebhookSignature."""
    sig = "ts=1717000000,v1=deadbeef"
    validator = WebhookSignatureValidator("meu-segredo")
    with pytest.raises(InvalidWebhookSignature):
        validator.validate("pay-123", "req-abc", sig)


def test_segredo_diferente_falha():
    """Assinatura gerada com segredo errado é rejeitada."""
    sig = _make_signature("segredo-errado", "pay-123", "req-abc", "1717000000")
    validator = WebhookSignatureValidator("segredo-correto")
    with pytest.raises(InvalidWebhookSignature):
        validator.validate("pay-123", "req-abc", sig)


def test_campo_ts_ausente_falha():
    """Header sem campo 'ts' levanta InvalidWebhookSignature."""
    validator = WebhookSignatureValidator("segredo")
    with pytest.raises(InvalidWebhookSignature, match="ts"):
        validator.validate("pay-123", "req-abc", "v1=abc123")


def test_campo_v1_ausente_falha():
    """Header sem campo 'v1' levanta InvalidWebhookSignature."""
    validator = WebhookSignatureValidator("segredo")
    with pytest.raises(InvalidWebhookSignature, match="v1"):
        validator.validate("pay-123", "req-abc", "ts=1717000000")
