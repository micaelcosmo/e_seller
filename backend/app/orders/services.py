"""Serviços de pedidos: criação (com preço congelado), leitura e listagem admin."""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import Product
from app.catalog.services import ProductCatalog
from app.coupons.services import CouponService
from app.orders.models import Order, OrderItem, OrderStatus
from app.payments.services import CheckoutService


class OrderNotFound(Exception):
    """Levantada quando um pedido não é encontrado pela referência."""


class OrderCancellationNotAllowed(Exception):
    """Levantada ao tentar cancelar um pedido já pago ou já cancelado."""


class OrderCreator:
    """Cria um pedido pendente (congelando o preço) e inicia o checkout."""

    def __init__(
        self,
        session: AsyncSession,
        catalog: ProductCatalog,
        checkout: CheckoutService,
        coupons: CouponService,
    ) -> None:
        """Recebe sessão, catálogo, checkout e serviço de cupom por injeção."""
        self.session = session
        self.catalog = catalog
        self.checkout = checkout
        self.coupons = coupons

    async def create(
        self,
        product_slug: str,
        buyer_email: str,
        user_id: int | None = None,
        coupon_code: str | None = None,
    ) -> Order:
        """Cria um pedido de 1 item (preço congelado), aplica cupom e checkout."""
        product = await self.catalog.get_by_slug(product_slug)
        return await self.create_from_items(
            buyer_email, [product], user_id, coupon_code
        )

    async def create_from_items(
        self,
        buyer_email: str,
        products: list[Product],
        user_id: int | None = None,
        coupon_code: str | None = None,
    ) -> Order:
        """Cria um pedido com vários itens (preço congelado), cupom e checkout."""
        order = Order(buyer_email=buyer_email, amount=Decimal("0.00"), user_id=user_id)
        total = Decimal("0.00")
        for product in products:
            order.items.append(
                OrderItem(product_id=product.id, unit_price=product.price, quantity=1)
            )
            total = total + Decimal(str(product.price))
        order.amount = total
        self.session.add(order)
        await self.session.flush()
        if coupon_code:
            await self.coupons.apply_to_order(coupon_code, order)
        checkout_data = self.checkout.create_for(order)
        # Atributo transitório (não persistido); usado só na serialização da resposta.
        order.checkout_url = checkout_data.checkout_url
        return order


class OrderReader:
    """Consulta pedidos pela referência pública."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def get_by_reference(self, reference: str) -> Order:
        """Retorna o pedido pela referência; levanta OrderNotFound se ausente."""
        statement = select(Order).where(Order.reference == reference)
        result = await self.session.scalars(statement)
        order = result.first()
        if order is None:
            raise OrderNotFound(reference)
        return order


class OrderAdminLister:
    """Lista pedidos para a área administrativa com paginação e filtro de status."""

    _PAGE_SIZE_MAX = 100

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    def _base_statement(
        self,
        status: str | None,
        query: str | None,
        reference: str | None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> object:
        """Constrói o statement base com os filtros aplicados (sem paginação).

        date_from e date_to devem ser strings ISO 8601 (ex.: '2026-01-01').
        """
        from datetime import UTC, datetime

        stmt = select(Order)
        if status is not None:
            try:
                status_value = OrderStatus(status)
            except ValueError:
                return None
            stmt = stmt.where(Order.status == status_value)
        if query is not None:
            pattern = f"%{query.lower()}%"
            stmt = stmt.where(func.lower(Order.buyer_email).like(pattern))
        if reference is not None:
            stmt = stmt.where(Order.reference == reference)
        if date_from is not None:
            try:
                dt_from = datetime.fromisoformat(date_from).replace(tzinfo=UTC)
                stmt = stmt.where(Order.created_at >= dt_from)
            except ValueError:
                return None
        if date_to is not None:
            try:
                dt_to = datetime.fromisoformat(date_to).replace(tzinfo=UTC)
                stmt = stmt.where(Order.created_at <= dt_to)
            except ValueError:
                return None
        return stmt

    async def list_orders(
        self,
        status: str | None,
        page: int,
        page_size: int,
        query: str | None = None,
        reference: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[Order]:
        """Retorna página de pedidos (mais recentes primeiro).

        Filtra por status, e-mail (ILIKE), referência e intervalo de datas.
        Limita page_size ao máximo permitido.
        """
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = self._base_statement(status, query, reference, date_from, date_to)
        if stmt is None:
            return []
        stmt = stmt.order_by(Order.id.desc())
        stmt = stmt.offset((page - 1) * effective_size).limit(effective_size)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def count_orders(
        self,
        status: str | None,
        query: str | None = None,
        reference: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> int:
        """Retorna o total de pedidos com os filtros aplicados (para X-Total-Count)."""
        base = self._base_statement(status, query, reference, date_from, date_to)
        if base is None:
            return 0
        count_stmt = select(func.count()).select_from(base.subquery())
        result = await self.session.scalar(count_stmt)
        return int(result or 0)


class TopProductsService:
    """Calcula o ranking dos produtos mais vendidos por volume de itens pagos."""

    _DEFAULT_LIMIT = 10

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def top_products(self, limit: int = _DEFAULT_LIMIT) -> list[dict]:
        """Retorna os produtos mais vendidos (pedidos com status PAID).

        Cada item do resultado contém product_id, title (via JOIN) e units_sold.
        """
        stmt = (
            select(
                OrderItem.product_id,
                Product.title,
                func.count(OrderItem.id).label("units_sold"),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .join(Product, Product.id == OrderItem.product_id)
            .where(Order.status == OrderStatus.PAID)
            .group_by(OrderItem.product_id, Product.title)
            .order_by(func.count(OrderItem.id).desc())
            .limit(limit)
        )
        rows = await self.session.execute(stmt)
        result = []
        for row in rows.all():
            result.append(
                {
                    "product_id": row.product_id,
                    "title": row.title,
                    "units_sold": row.units_sold,
                }
            )
        return result


class OrderCanceller:
    """Cancela um pedido PENDING do comprador (auto-serviço)."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def cancel(self, reference: str, user_id: int) -> Order:
        """Cancela o pedido identificado pela referência.

        Levanta OrderNotFound se o pedido não existir ou não pertencer ao usuário.
        Levanta OrderCancellationNotAllowed se o status não for PENDING.
        """
        result = await self.session.scalars(
            select(Order).where(Order.reference == reference, Order.user_id == user_id)
        )
        order = result.first()
        if order is None:
            raise OrderNotFound(reference)
        if order.status != OrderStatus.PENDING:
            raise OrderCancellationNotAllowed(order.status.value)
        order.status = OrderStatus.CANCELLED
        await self.session.flush()
        return order


class UserOrderLister:
    """Lista os pedidos de um usuário autenticado."""

    _PAGE_SIZE_MAX = 50

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def list_for_user(
        self,
        user_id: int,
        page: int,
        page_size: int,
        status: str | None = None,
    ) -> list[Order]:
        """Retorna pedidos do usuário (mais recentes primeiro) com paginação.

        Filtro opcional por status (ex.: 'paid', 'pending').
        Limita page_size ao máximo permitido para evitar consultas excessivas.
        """
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = select(Order).where(Order.user_id == user_id)
        if status is not None:
            try:
                status_value = OrderStatus(status)
                stmt = stmt.where(Order.status == status_value)
            except ValueError:
                return []
        stmt = (
            stmt.order_by(Order.id.desc())
            .offset((page - 1) * effective_size)
            .limit(effective_size)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())
