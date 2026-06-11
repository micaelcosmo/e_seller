"""Máquina de estados do pedido: garante transições válidas."""

from app.orders.models import Order, OrderStatus


class InvalidTransition(Exception):
    """Levantada ao tentar uma transição de estado não permitida."""


class OrderStateMachine:
    """Aplica transições válidas sobre um pedido."""

    _ALLOWED = {
        OrderStatus.PENDING: {
            OrderStatus.PAID,
            OrderStatus.FAILED,
            OrderStatus.CANCELLED,
        },
        OrderStatus.PAID: {OrderStatus.REFUNDED},
        OrderStatus.FAILED: set(),
        OrderStatus.CANCELLED: set(),
        OrderStatus.REFUNDED: set(),
    }

    def __init__(self, order: Order) -> None:
        """Recebe o pedido cujo estado será controlado."""
        self.order = order

    def _transition(self, target: OrderStatus) -> None:
        """Valida e aplica a transição para `target` (uso interno)."""
        allowed = self._ALLOWED.get(self.order.status, set())
        if target not in allowed:
            raise InvalidTransition(f"{self.order.status} -> {target}")
        self.order.status = target

    def mark_paid(self) -> None:
        """Transiciona o pedido de PENDING para PAID."""
        self._transition(OrderStatus.PAID)

    def mark_failed(self) -> None:
        """Transiciona o pedido de PENDING para FAILED."""
        self._transition(OrderStatus.FAILED)

    def cancel(self) -> None:
        """Transiciona o pedido de PENDING para CANCELLED."""
        self._transition(OrderStatus.CANCELLED)

    def refund(self) -> None:
        """Transiciona o pedido de PAID para REFUNDED."""
        self._transition(OrderStatus.REFUNDED)
