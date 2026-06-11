"""Mapeamento do status do provedor para o estado interno do pedido."""

from app.orders.models import OrderStatus


class UnknownProviderStatus(Exception):
    """Levantada quando o status do provedor não é reconhecido."""


class StatusMapper:
    """Traduz o status do provedor de pagamento para OrderStatus."""

    _MAP = {
        "approved": OrderStatus.PAID,
        "pending": OrderStatus.PENDING,
        "in_process": OrderStatus.PENDING,
        "rejected": OrderStatus.FAILED,
        "cancelled": OrderStatus.CANCELLED,
        "refunded": OrderStatus.REFUNDED,
        "charged_back": OrderStatus.REFUNDED,
    }

    def to_order_status(self, provider_status: str) -> OrderStatus:
        """Retorna o OrderStatus correspondente; levanta erro se desconhecido."""
        mapped = self._MAP.get(provider_status)
        if mapped is None:
            raise UnknownProviderStatus(provider_status)
        return mapped
