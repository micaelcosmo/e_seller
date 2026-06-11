"""Serviços de posse: conceder, listar a biblioteca e reemitir download (async)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import Product
from app.delivery.models import DownloadGrant
from app.delivery.services import DownloadIssuer
from app.entitlement.models import Entitlement
from app.orders.models import Order, OrderItem


class NotOwned(Exception):
    """Levantada quando o usuário não possui o e-book solicitado."""


class EntitlementService:
    """Gerencia a posse de e-books (direito perpétuo do usuário)."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def grant_for_order(self, order: Order) -> None:
        """Concede posse de cada item ao usuário do pedido (se houver conta)."""
        if order.user_id is None:
            return
        for item in order.items:
            if await self._owns(order.user_id, item.product_id):
                continue
            self.session.add(
                Entitlement(
                    user_id=order.user_id,
                    product_id=item.product_id,
                    order_item_id=item.id,
                )
            )
        await self.session.flush()

    async def revoke_for_order(self, order: Order) -> int:
        """Revoga a posse de cada item do pedido (anti-pirataria no estorno)."""
        revoked = 0
        for item in order.items:
            result = await self.session.scalars(
                select(Entitlement).where(
                    Entitlement.order_item_id == item.id,
                )
            )
            for entitlement in result.all():
                await self.session.delete(entitlement)
                revoked = revoked + 1
        await self.session.flush()
        return revoked

    async def library(self, user_id: int) -> list[Product]:
        """Lista os e-books possuídos pelo usuário."""
        statement = (
            select(Product)
            .join(Entitlement, Entitlement.product_id == Product.id)
            .where(Entitlement.user_id == user_id)
            .order_by(Entitlement.created_at.desc())
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def reissue_download(
        self, user_id: int, slug: str, issuer: DownloadIssuer
    ) -> DownloadGrant:
        """Reemite um link de download de um e-book possuído pelo usuário."""
        product = await self.session.scalars(
            select(Product).where(Product.slug == slug)
        )
        found = product.first()
        if found is None:
            raise NotOwned(slug)
        entitlement = await self.session.scalars(
            select(Entitlement).where(
                Entitlement.user_id == user_id,
                Entitlement.product_id == found.id,
            )
        )
        owned = entitlement.first()
        if owned is None:
            raise NotOwned(slug)
        order_item = await self.session.get(OrderItem, owned.order_item_id)
        return await issuer.issue_for(order_item)

    async def _owns(self, user_id: int, product_id: int) -> bool:
        """Verifica se o usuário já possui o produto."""
        result = await self.session.scalars(
            select(Entitlement).where(
                Entitlement.user_id == user_id,
                Entitlement.product_id == product_id,
            )
        )
        return result.first() is not None
