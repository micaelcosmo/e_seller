"""SearchService: busca full-text com fallback ILIKE para SQLite/testes."""

from __future__ import annotations

from sqlalchemy import func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import Product, ProductStatus


class SearchService:
    """Busca por produtos com suporte a FTS (PostgreSQL) ou ILIKE (SQLite).

    Detecta o dialeto em tempo de execução; usa to_tsvector/plainto_tsquery
    no PostgreSQL e func.lower().like() no SQLite ou qualquer outro dialeto.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção de dependência."""
        self.session = session

    def _is_postgres(self) -> bool:
        """Retorna True se o engine for PostgreSQL."""
        dialect = self.session.get_bind().dialect.name  # type: ignore[union-attr]
        return dialect == "postgresql"

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """Busca produtos publicados pelo texto da consulta.

        No PostgreSQL: usa plainto_tsquery com ranking ts_rank.
        No SQLite: fallback com ILIKE em título, autor e descrição.
        """
        from sqlalchemy import select

        stmt = select(Product).where(Product.status == ProductStatus.PUBLISHED)
        if self._is_postgres():
            stmt = stmt.where(
                text(
                    "to_tsvector('portuguese', coalesce(product.title,'') || ' '"
                    " || coalesce(product.author,'') || ' '"
                    " || coalesce(product.description,''))"
                    " @@ plainto_tsquery('portuguese', :q)"
                )
            ).params(q=query)
        else:
            pattern = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Product.title).like(pattern),
                    func.lower(Product.author).like(pattern),
                    func.lower(Product.description).like(pattern),
                )
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.scalars(stmt)
        return list(result.all())
