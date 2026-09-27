"""Repositório de acesso ao banco de dados para o catálogo de produtos."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import (
    Author,
    Category,
    Product,
    ProductStatus,
    Tag,
    product_author,
    product_tag,
)


class ProductRepository:
    """Encapsula as consultas SQL do catálogo (sem lógica de negócio)."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção de dependência."""
        self.session = session

    # Mapeamento de valores aceitos para o parâmetro sort.
    _SORT_COLUMNS = {
        "newest": Product.created_at.desc(),
        "oldest": Product.created_at.asc(),
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "title_asc": Product.title.asc(),
    }
    _SORT_DEFAULT = "newest"

    async def list_published(
        self,
        query: str | None = None,
        skip: int = 0,
        limit: int = 20,
        tag_slug: str | None = None,
        author_slug: str | None = None,
        sort: str | None = None,
        featured: bool | None = None,
        price_min: Decimal | None = None,
        price_max: Decimal | None = None,
    ) -> list[Product]:
        """Lista produtos publicados com paginação, filtros e ordenação opcionais."""
        statement = self.build_list_statement(
            query, skip, limit, tag_slug, author_slug, sort, featured,
            price_min, price_max,
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    def build_list_statement(
        self,
        query: str | None = None,
        skip: int = 0,
        limit: int = 20,
        tag_slug: str | None = None,
        author_slug: str | None = None,
        sort: str | None = None,
        featured: bool | None = None,
        price_min: Decimal | None = None,
        price_max: Decimal | None = None,
    ):
        """Monta o SELECT da listagem publicada (sem executar).

        Tag e autor filtram por subconsulta `IN`, não por join: cada produto sai
        uma vez só, sem `DISTINCT` — que no Postgres impediria ordenar pela
        relevância da busca (expressão fora do select).
        """
        statement = select(Product).where(Product.status == ProductStatus.PUBLISHED)
        if featured is not None:
            statement = statement.where(Product.featured == featured)
        if price_min is not None:
            statement = statement.where(Product.price >= price_min)
        if price_max is not None:
            statement = statement.where(Product.price <= price_max)
        relevance = None
        if query:
            pattern = f"%{query.lower()}%"
            starts_pattern = f"{query.lower()}%"
            statement = statement.where(
                or_(
                    func.lower(Product.title).like(pattern),
                    func.lower(Product.author).like(pattern),
                    func.lower(Product.description).like(pattern),
                )
            )
            # Relevância: começa com > contém no título > contém em outros campos.
            relevance = case(
                (func.lower(Product.title).like(starts_pattern), 3),
                (func.lower(Product.title).like(pattern), 2),
                else_=1,
            )
        if tag_slug:
            tagged = (
                select(product_tag.c.product_id)
                .join(Tag, Tag.id == product_tag.c.tag_id)
                .where(Tag.slug == tag_slug)
            )
            statement = statement.where(Product.id.in_(tagged))
        if author_slug:
            authored = (
                select(product_author.c.product_id)
                .join(Author, Author.id == product_author.c.author_id)
                .where(Author.slug == author_slug)
            )
            statement = statement.where(Product.id.in_(authored))
        order_col = self._SORT_COLUMNS.get(sort or self._SORT_DEFAULT)
        if order_col is None:
            order_col = self._SORT_COLUMNS[self._SORT_DEFAULT]
        if relevance is not None and sort is None:
            statement = statement.order_by(relevance.desc(), order_col)
        else:
            statement = statement.order_by(order_col)
        return statement.offset(skip).limit(limit)

    async def count_published(
        self,
        query: str | None = None,
        tag_slug: str | None = None,
        author_slug: str | None = None,
        price_min: Decimal | None = None,
        price_max: Decimal | None = None,
    ) -> int:
        """Conta o total de produtos publicados com os mesmos filtros da listagem."""
        stmt = (
            select(func.count(Product.id.distinct()))
            .where(Product.status == ProductStatus.PUBLISHED)
        )
        if price_min is not None:
            stmt = stmt.where(Product.price >= price_min)
        if price_max is not None:
            stmt = stmt.where(Product.price <= price_max)
        if query:
            pattern = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Product.title).like(pattern),
                    func.lower(Product.author).like(pattern),
                    func.lower(Product.description).like(pattern),
                )
            )
        if tag_slug:
            stmt = (
                stmt
                .join(product_tag, product_tag.c.product_id == Product.id)
                .join(Tag, Tag.id == product_tag.c.tag_id)
                .where(Tag.slug == tag_slug)
            )
        if author_slug:
            stmt = (
                stmt
                .join(product_author, product_author.c.product_id == Product.id)
                .join(Author, Author.id == product_author.c.author_id)
                .where(Author.slug == author_slug)
            )
        result = await self.session.scalar(stmt)
        return result or 0

    async def get_published_by_slug(self, slug: str) -> Product | None:
        """Retorna o produto publicado pelo slug (ou None se ausente)."""
        statement = select(Product).where(
            Product.slug == slug,
            Product.status == ProductStatus.PUBLISHED,
        )
        result = await self.session.scalars(statement)
        return result.first()

    async def find_related(
        self, product: Product, limit: int = 4
    ) -> list[Product]:
        """Busca produtos publicados relacionados (mesmo autor ou mesma tag).

        Exclui o próprio produto; ordena por número de tags em comum (DESC).
        """
        from sqlalchemy import literal, union_all

        author_ids_stmt = (
            select(product_author.c.author_id)
            .where(product_author.c.product_id == product.id)
            .scalar_subquery()
        )
        tag_ids_stmt = (
            select(product_tag.c.tag_id)
            .where(product_tag.c.product_id == product.id)
            .scalar_subquery()
        )
        # Candidatos por autor compartilhado.
        by_author = (
            select(
                product_author.c.product_id.label("product_id"),
                literal(2).label("score"),
            )
            .where(product_author.c.author_id.in_(author_ids_stmt))
            .where(product_author.c.product_id != product.id)
        )
        # Candidatos por tag compartilhada.
        by_tag = (
            select(
                product_tag.c.product_id.label("product_id"),
                literal(1).label("score"),
            )
            .where(product_tag.c.tag_id.in_(tag_ids_stmt))
            .where(product_tag.c.product_id != product.id)
        )
        union_cte = union_all(by_author, by_tag).cte("candidates")
        ranked = (
            select(
                union_cte.c.product_id,
                func.sum(union_cte.c.score).label("total_score"),
            )
            .group_by(union_cte.c.product_id)
            .order_by(func.sum(union_cte.c.score).desc())
            .limit(limit)
            .cte("ranked")
        )
        stmt = (
            select(Product)
            .join(ranked, ranked.c.product_id == Product.id)
            .where(Product.status == ProductStatus.PUBLISHED)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def slug_exists(self, slug: str) -> bool:
        """Verifica se um slug já está em uso (qualquer status)."""
        result = await self.session.scalars(
            select(Product).where(Product.slug == slug)
        )
        return result.first() is not None

    async def resolve_category_id(self, category_slug: str | None) -> int | None:
        """Retorna o id da categoria pelo slug (ou None se ausente/não encontrado)."""
        if not category_slug:
            return None
        result = await self.session.scalars(
            select(Category).where(Category.slug == category_slug)
        )
        category = result.first()
        return category.id if category is not None else None
