"""Gateways de pagamento: abstração (Protocol) e implementação fake (sem conta)."""

from dataclasses import dataclass
from typing import Protocol

from app.orders.models import Order


@dataclass(frozen=True)
class CheckoutData:
    """Dados do checkout criado no provedor."""

    checkout_url: str


@dataclass(frozen=True)
class PaymentData:
    """Dados de um pagamento consultado no provedor."""

    provider_payment_id: str
    status: str


class PaymentGateway(Protocol):
    """Contrato de um provedor de pagamento (permite trocar/implementar fakes)."""

    def create_checkout(self, order: Order) -> CheckoutData:
        """Cria um checkout para o pedido e retorna a URL de pagamento."""
        ...


class FakePaymentGateway:
    """Provedor fake: gera um checkout que aponta para o simulador local (sem conta)."""

    def __init__(self, base_url: str) -> None:
        """Recebe a URL base usada para montar o link do simulador."""
        self.base_url = base_url

    def create_checkout(self, order: Order) -> CheckoutData:
        """Monta a URL do simulador de pagamento para a referência do pedido."""
        url = f"{self.base_url}/pay/simulate/{order.reference}"
        return CheckoutData(checkout_url=url)
