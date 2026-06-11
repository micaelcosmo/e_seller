"""Serviço de taxonomia do catálogo: autores, editora, série e tags (async)."""

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import (
    Author,
    Product,
    ProductStatus,
    Publisher,
    Series,
    Tag,
    product_author,
    product_tag,
)
from app.catalog.schemas import TaxonomyLabel
from app.core.text import Slugifier


class TaxonomyService:
    """Resolve/cria entidades de taxonomia e as associa a um produto."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção e prepara o gerador de slug."""
        self.session = session
        self.slugifier = Slugifier(fallback="tag")

    async def get_or_create_author(self, name: str) -> Author:
        """Retorna o autor pelo nome (criando-o se ainda não existir)."""
        slug = self.slugifier.slugify(name)
        existing = await self._find(Author, slug)
        if existing is not None:
            return existing
        author = Author(name=name.strip(), slug=slug)
        self.session.add(author)
        await self.session.flush()
        return author

    async def get_or_create_publisher(self, name: str) -> Publisher:
        """Retorna a editora pelo nome (criando-a se ainda não existir)."""
        slug = self.slugifier.slugify(name)
        existing = await self._find(Publisher, slug)
        if existing is not None:
            return existing
        publisher = Publisher(name=name.strip(), slug=slug)
        self.session.add(publisher)
        await self.session.flush()
        return publisher

    async def get_or_create_series(self, name: str) -> Series:
        """Retorna a série pelo nome (criando-a se ainda não existir)."""
        slug = self.slugifier.slugify(name)
        existing = await self._find(Series, slug)
        if existing is not None:
            return existing
        series = Series(name=name.strip(), slug=slug)
        self.session.add(series)
        await self.session.flush()
        return series

    async def get_or_create_tag(self, name: str) -> Tag:
        """Retorna a tag pelo nome (criando-a se ainda não existir)."""
        slug = self.slugifier.slugify(name)
        existing = await self._find(Tag, slug)
        if existing is not None:
            return existing
        tag = Tag(name=name.strip(), slug=slug)
        self.session.add(tag)
        await self.session.flush()
        return tag

    async def apply_to_product(
        self,
        product: Product,
        authors: list[str],
        publisher: str | None,
        series: str | None,
        tags: list[str],
    ) -> None:
        """Associa autores, editora, série e tags ao produto (criando o que faltar).

        As coleções e relações são atribuídas por completo (mesmo vazias) enquanto
        o produto ainda é transitório, marcando-as como carregadas. Assim a
        serialização posterior não dispara um lazy-load implícito (proibido em async).
        """
        resolved_authors = []
        for author_name in authors:
            if author_name.strip():
                resolved_authors.append(await self.get_or_create_author(author_name))
        product.authors = resolved_authors

        resolved_tags = []
        for tag_name in tags:
            if tag_name.strip():
                resolved_tags.append(await self.get_or_create_tag(tag_name))
        product.tags = resolved_tags

        product.publisher = None
        if publisher and publisher.strip():
            product.publisher = await self.get_or_create_publisher(publisher)

        product.series = None
        if series and series.strip():
            product.series = await self.get_or_create_series(series)

    async def list_authors(self) -> list[TaxonomyLabel]:
        """Lista autores com contagem de produtos publicados (ordem alfabética)."""
        stmt = (
            select(
                Author.name,
                Author.slug,
                func.count(Product.id).label("count"),
            )
            .outerjoin(
                product_author,
                product_author.c.author_id == Author.id,
            )
            .outerjoin(
                Product,
                and_(
                    product_author.c.product_id == Product.id,
                    Product.status == ProductStatus.PUBLISHED,
                ),
            )
            .group_by(Author.id, Author.name, Author.slug)
            .order_by(Author.name)
        )
        rows = await self.session.execute(stmt)
        return [
            TaxonomyLabel(name=r.name, slug=r.slug, count=r.count)
            for r in rows
        ]

    async def list_tags(self) -> list[TaxonomyLabel]:
        """Lista tags com contagem de produtos publicados (ordem alfabética)."""
        stmt = (
            select(
                Tag.name,
                Tag.slug,
                func.count(Product.id).label("count"),
            )
            .outerjoin(
                product_tag,
                product_tag.c.tag_id == Tag.id,
            )
            .outerjoin(
                Product,
                and_(
                    product_tag.c.product_id == Product.id,
                    Product.status == ProductStatus.PUBLISHED,
                ),
            )
            .group_by(Tag.id, Tag.name, Tag.slug)
            .order_by(Tag.name)
        )
        rows = await self.session.execute(stmt)
        return [
            TaxonomyLabel(name=r.name, slug=r.slug, count=r.count)
            for r in rows
        ]

    async def _find(self, model: type, slug: str):
        """Busca uma entidade de taxonomia pelo slug (ou None)."""
        result = await self.session.scalars(
            select(model).where(model.slug == slug)
        )
        return result.first()
