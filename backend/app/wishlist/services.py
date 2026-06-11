"""Serviço de wishlist: adicionar, remover e listar (async)."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import Product, ProductStatus
from app.wishlist.models import Wishlist, WishlistItem


class WishlistProductNotFound(Exception):
    """Levantada quando o produto não existe ou não está publicado."""


class WishlistService:
    """Gerencia a lista de desejos de um usuário."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def add(self, user_id: int, slug: str) -> None:
        """Adiciona um produto à wishlist (idempotente)."""
        product = await self._published_by_slug(slug)
        wishlist = await self._get_or_create(user_id)
        if await self._has_item(wishlist.id, product.id):
            return
        self.session.add(
            WishlistItem(wishlist_id=wishlist.id, product_id=product.id)
        )
        await self.session.flush()

    async def remove(self, user_id: int, slug: str) -> None:
        """Remove um produto da wishlist."""
        product = await self._published_by_slug(slug)
        wishlist = await self._get_or_create(user_id)
        await self.session.execute(
            delete(WishlistItem).where(
                WishlistItem.wishlist_id == wishlist.id,
                WishlistItem.product_id == product.id,
            )
        )
        await self.session.flush()

    async def items(self, user_id: int) -> list[Product]:
        """Lista os produtos na wishlist do usuário."""
        statement = (
            select(Product)
            .join(WishlistItem, WishlistItem.product_id == Product.id)
            .join(Wishlist, Wishlist.id == WishlistItem.wishlist_id)
            .where(Wishlist.user_id == user_id)
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def _published_by_slug(self, slug: str) -> Product:
        """Busca o produto publicado pelo slug."""
        result = await self.session.scalars(
            select(Product).where(
                Product.slug == slug,
                Product.status == ProductStatus.PUBLISHED,
            )
        )
        product = result.first()
        if product is None:
            raise WishlistProductNotFound(slug)
        return product

    async def _get_or_create(self, user_id: int) -> Wishlist:
        """Retorna a wishlist do usuário, criando se necessário."""
        result = await self.session.scalars(
            select(Wishlist).where(Wishlist.user_id == user_id)
        )
        wishlist = result.first()
        if wishlist is None:
            wishlist = Wishlist(user_id=user_id)
            self.session.add(wishlist)
            await self.session.flush()
        return wishlist

    async def _has_item(self, wishlist_id: int, product_id: int) -> bool:
        """Verifica se o produto já está na wishlist."""
        result = await self.session.scalars(
            select(WishlistItem).where(
                WishlistItem.wishlist_id == wishlist_id,
                WishlistItem.product_id == product_id,
            )
        )
        return result.first() is not None
