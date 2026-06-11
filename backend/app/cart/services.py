"""Serviço de carrinho: adicionar, remover, listar e limpar (async)."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cart.models import Cart, CartItem
from app.catalog.models import Product, ProductStatus
from app.entitlement.models import Entitlement


class CartProductNotFound(Exception):
    """Levantada quando o produto não existe ou não está publicado."""


class AlreadyOwned(Exception):
    """Levantada ao tentar carregar um e-book que o usuário já possui."""


class CartService:
    """Gerencia o carrinho de um usuário."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def add(self, user_id: int, slug: str) -> None:
        """Adiciona um produto ao carrinho (idempotente); recusa se já possuído."""
        product = await self._published_by_slug(slug)
        if await self._owns(user_id, product.id):
            raise AlreadyOwned(slug)
        cart = await self._get_or_create_cart(user_id)
        if await self._has_item(cart.id, product.id):
            return
        self.session.add(CartItem(cart_id=cart.id, product_id=product.id))
        await self.session.flush()

    async def remove(self, user_id: int, slug: str) -> None:
        """Remove um produto do carrinho."""
        product = await self._published_by_slug(slug)
        cart = await self._get_or_create_cart(user_id)
        await self.session.execute(
            delete(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product.id,
            )
        )
        await self.session.flush()

    async def items(self, user_id: int) -> list[Product]:
        """Lista os produtos no carrinho do usuário."""
        statement = (
            select(Product)
            .join(CartItem, CartItem.product_id == Product.id)
            .join(Cart, Cart.id == CartItem.cart_id)
            .where(Cart.user_id == user_id)
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def clear(self, user_id: int) -> None:
        """Esvazia o carrinho do usuário."""
        cart = await self._get_or_create_cart(user_id)
        await self.session.execute(
            delete(CartItem).where(CartItem.cart_id == cart.id)
        )
        await self.session.flush()

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
            raise CartProductNotFound(slug)
        return product

    async def _get_or_create_cart(self, user_id: int) -> Cart:
        """Retorna o carrinho do usuário, criando se necessário."""
        result = await self.session.scalars(
            select(Cart).where(Cart.user_id == user_id)
        )
        cart = result.first()
        if cart is None:
            cart = Cart(user_id=user_id)
            self.session.add(cart)
            await self.session.flush()
        return cart

    async def _has_item(self, cart_id: int, product_id: int) -> bool:
        """Verifica se o produto já está no carrinho."""
        result = await self.session.scalars(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
        )
        return result.first() is not None

    async def _owns(self, user_id: int, product_id: int) -> bool:
        """Verifica se o usuário já possui o produto."""
        result = await self.session.scalars(
            select(Entitlement).where(
                Entitlement.user_id == user_id,
                Entitlement.product_id == product_id,
            )
        )
        return result.first() is not None
