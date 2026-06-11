"""Serviços de pagamento: criação de checkout e processamento do webhook (async)."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import Product
from app.core.clock import Clock
from app.core.email import EmailService
from app.delivery.services import DownloadIssuer
from app.entitlement.services import EntitlementService
from app.orders.models import Order, OrderItem, OrderStatus
from app.orders.state_machine import OrderStateMachine
from app.payments.gateways import CheckoutData, PaymentGateway
from app.payments.models import Payment
from app.payments.status_map import StatusMapper


@dataclass(frozen=True)
class WebhookNotification:
    """Notificação de pagamento recebida (já autenticada na borda)."""

    provider_payment_id: str
    order_reference: str
    provider_status: str


@dataclass(frozen=True)
class WebhookResult:
    """Resultado do processamento de um webhook."""

    outcome: str
    order_reference: str | None


class CheckoutService:
    """Cria o checkout de um pedido delegando ao gateway de pagamento."""

    def __init__(self, gateway: PaymentGateway) -> None:
        """Recebe o gateway (abstração) por injeção de dependência."""
        self.gateway = gateway

    def create_for(self, order: Order) -> CheckoutData:
        """Cria o checkout e retorna os dados (inclui a URL de pagamento)."""
        return self.gateway.create_checkout(order)


class WebhookProcessor:
    """Processa notificações de pagamento de forma idempotente (async)."""

    def __init__(
        self,
        session: AsyncSession,
        status_mapper: StatusMapper,
        download_issuer: DownloadIssuer,
        clock: Clock,
        entitlements: EntitlementService,
        email_service: EmailService | None = None,
    ) -> None:
        """Recebe as dependências necessárias por injeção."""
        self.session = session
        self.status_mapper = status_mapper
        self.download_issuer = download_issuer
        self.clock = clock
        self.entitlements = entitlements
        self.email_service = email_service

    async def process(self, notification: WebhookNotification) -> WebhookResult:
        """Aplica a notificação: confirma pagamento e libera entrega se aprovado."""
        if await self._already_processed(notification.provider_payment_id):
            return WebhookResult("ALREADY_PROCESSED", notification.order_reference)

        order = await self._find_order(notification.order_reference)
        if order is None:
            return WebhookResult("IGNORED", notification.order_reference)

        target = self.status_mapper.to_order_status(notification.provider_status)
        self._record_payment(order, notification)
        await self._apply_transition(order, target)
        await self.session.flush()
        return WebhookResult("APPLIED", order.reference)

    async def _already_processed(self, provider_payment_id: str) -> bool:
        """Verifica se já existe pagamento com aquele id (idempotência)."""
        statement = select(Payment).where(
            Payment.provider_payment_id == provider_payment_id
        )
        result = await self.session.scalars(statement)
        return result.first() is not None

    async def _find_order(self, reference: str) -> Order | None:
        """Busca o pedido pela referência pública."""
        statement = select(Order).where(Order.reference == reference)
        result = await self.session.scalars(statement)
        return result.first()

    def _record_payment(
        self, order: Order, notification: WebhookNotification
    ) -> None:
        """Persiste o registro de pagamento (auditoria + idempotência)."""
        payment = Payment(
            order_id=order.id,
            provider="fake",
            provider_payment_id=notification.provider_payment_id,
            status=notification.provider_status,
            processed_at=self.clock.now(),
        )
        self.session.add(payment)

    async def _apply_transition(self, order: Order, target: OrderStatus) -> None:
        """Aplica a transição de estado e emite grants quando aprovado."""
        machine = OrderStateMachine(order)
        if target == OrderStatus.PAID and order.status == OrderStatus.PENDING:
            machine.mark_paid()
            await self._issue_grants(order)
            await self.entitlements.grant_for_order(order)
            await self._notify_buyer(order)
        elif target == OrderStatus.FAILED and order.status == OrderStatus.PENDING:
            machine.mark_failed()

    async def _issue_grants(self, order: Order) -> None:
        """Emite um DownloadGrant para cada item do pedido."""
        for item in order.items:
            await self.download_issuer.issue_for(item)

    async def _notify_buyer(self, order: Order) -> None:
        """Envia e-mail de confirmação ao comprador (falha silenciosa).

        Busca os títulos dos produtos via query para evitar lazy-load implícito.
        """
        if self.email_service is None:
            return
        items_result = await self.session.scalars(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order_items = list(items_result.all())
        product_ids = [i.product_id for i in order_items]
        if product_ids:
            products_result = await self.session.scalars(
                select(Product).where(Product.id.in_(product_ids))
            )
            titles = [p.title for p in products_result.all()]
        else:
            titles = []
        product_title = ", ".join(titles) if titles else "e-book"
        self.email_service.send_purchase_confirmation(
            order.buyer_email, product_title, order.reference
        )
