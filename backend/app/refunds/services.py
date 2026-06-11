"""Serviço de estorno: registra o refund, marca o pedido e revoga a posse."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.delivery.services import GrantRevoker
from app.entitlement.services import EntitlementService
from app.orders.models import Order
from app.orders.state_machine import OrderStateMachine
from app.payments.models import Payment
from app.refunds.models import Refund, RefundStatus


class RefundNotAllowed(Exception):
    """Levantada quando o pedido não está em um estado estornável."""


class PaymentNotFound(Exception):
    """Levantada quando não há pagamento aprovado para o pedido."""


class RefundService:
    """Processa estornos de pedidos pagos (simulado; revoga a posse)."""

    # Estado do provedor que indica um pagamento efetivamente aprovado.
    _APPROVED_STATUS = "approved"

    def __init__(
        self,
        session: AsyncSession,
        entitlements: EntitlementService,
        grant_revoker: GrantRevoker,
    ) -> None:
        """Recebe a sessão, a posse e o invalidador de grants por injeção."""
        self.session = session
        self.entitlements = entitlements
        self.grant_revoker = grant_revoker

    async def refund_order(
        self, order: Order, amount: Decimal | None = None, reason: str = ""
    ) -> Refund:
        """Estorna o pedido pago: registra o refund, marca REFUNDED e revoga posse."""
        payment = await self._approved_payment(order.id)
        refund_amount = self._resolve_amount(order, amount)
        refund = Refund(
            payment_id=payment.id,
            order_id=order.id,
            amount=refund_amount,
            reason=reason.strip(),
            status=RefundStatus.COMPLETED,
        )
        self.session.add(refund)
        # Transição de estado validada (PAID -> REFUNDED).
        OrderStateMachine(order).refund()
        await self.entitlements.revoke_for_order(order)
        # Anti-pirataria: invalida também os links de download já emitidos.
        await self.grant_revoker.revoke_for_order(order)
        await self.session.flush()
        return refund

    async def _approved_payment(self, order_id: int) -> Payment:
        """Localiza o pagamento aprovado do pedido; senão levanta PaymentNotFound."""
        result = await self.session.scalars(
            select(Payment).where(
                Payment.order_id == order_id,
                Payment.status == self._APPROVED_STATUS,
            )
        )
        payment = result.first()
        if payment is None:
            raise PaymentNotFound(order_id)
        return payment

    def _resolve_amount(self, order: Order, amount: Decimal | None) -> Decimal:
        """Define o valor do estorno (total por padrão) e valida o limite."""
        total = Decimal(str(order.amount))
        if amount is None:
            return total
        requested = Decimal(str(amount))
        if requested <= Decimal("0") or requested > total:
            raise RefundNotAllowed(str(amount))
        return requested


class RefundAdminLister:
    """Lista estornos para a área administrativa com paginação."""

    _PAGE_SIZE_MAX = 100

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def list_refunds(self, page: int, page_size: int) -> list[Refund]:
        """Retorna página de estornos (mais recentes primeiro)."""
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = (
            select(Refund)
            .order_by(Refund.id.desc())
            .offset((page - 1) * effective_size)
            .limit(effective_size)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())
