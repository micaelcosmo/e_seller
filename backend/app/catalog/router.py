"""Rotas públicas do catálogo (API JSON)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.schemas import (
    ProductCountOut,
    ProductListItem,
    ProductOut,
    TaxonomyLabel,
)
from app.catalog.services import ProductCatalog
from app.catalog.taxonomy_service import TaxonomyService
from app.core.db import get_session

router = APIRouter(prefix="/api/v1", tags=["catalog"])


def get_product_catalog(session: AsyncSession = Depends(get_session)) -> ProductCatalog:
    """Constrói o serviço de catálogo com a sessão injetada."""
    return ProductCatalog(session)


def get_taxonomy_service(
    session: AsyncSession = Depends(get_session),
) -> TaxonomyService:
    """Constrói o serviço de taxonomia com a sessão injetada."""
    return TaxonomyService(session)


@router.get("/authors", response_model=list[TaxonomyLabel])
async def list_authors(
    taxonomy: TaxonomyService = Depends(get_taxonomy_service),
) -> list:
    """Lista os autores cadastrados (faceta de navegação)."""
    return await taxonomy.list_authors()


@router.get("/tags", response_model=list[TaxonomyLabel])
async def list_tags(
    taxonomy: TaxonomyService = Depends(get_taxonomy_service),
) -> list:
    """Lista as tags cadastradas (faceta de navegação)."""
    return await taxonomy.list_tags()


@router.get("/products/count", response_model=ProductCountOut)
async def count_products(
    q: str | None = None,
    tag: str | None = None,
    author: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    catalog: ProductCatalog = Depends(get_product_catalog),
) -> object:
    """Retorna o total de produtos publicados com os filtros ativos.

    Os parâmetros `page` e `page_size` são usados apenas para calcular `has_next`.
    """
    total = await catalog.count_published(q, tag, author)
    has_next = (page * page_size) < total
    return ProductCountOut(
        total=total, page=page, page_size=page_size, has_next=has_next
    )


@router.get("/products", response_model=list[ProductListItem])
async def list_products(
    q: str | None = None,
    tag: str | None = None,
    author: str | None = None,
    featured: bool | None = Query(default=None, description="Filtrar destaques"),
    sort: str | None = Query(
        default=None,
        description="Ordenação: newest | oldest | price_asc | price_desc | title_asc",
    ),
    page: int | None = Query(default=None, ge=1, description="Número da página"),
    page_size: int | None = Query(
        default=None, ge=1, le=100, description="Itens por página"
    ),
    skip: int = Query(default=0, ge=0, description="Offset (legado)"),
    limit: int = Query(default=20, ge=1, le=100, description="Limite (legado)"),
    catalog: ProductCatalog = Depends(get_product_catalog),
) -> list:
    """Lista produtos publicados com busca, filtros (featured, tag, author) e sort.

    Paginação via `page`/`page_size` (recomendado) ou `skip`/`limit` (legado).
    Quando `page` é informado, `skip` e `limit` são ignorados.
    """
    if page is not None:
        size = page_size if page_size is not None else 20
        effective_skip = (page - 1) * size
        effective_limit = size
    else:
        effective_skip = skip
        effective_limit = page_size if page_size is not None else limit
    return await catalog.list_published(
        q, effective_skip, effective_limit, tag, author, sort, featured
    )


@router.get("/products/{slug}/related", response_model=list[ProductListItem])
async def related_products(
    slug: str,
    catalog: ProductCatalog = Depends(get_product_catalog),
) -> list:
    """Retorna até 4 produtos relacionados (mesmo autor ou mesma tag)."""
    return await catalog.get_related(slug)


@router.get("/products/{slug}", response_model=ProductOut)
async def get_product(
    slug: str,
    catalog: ProductCatalog = Depends(get_product_catalog),
) -> object:
    """Retorna o detalhe de um produto publicado pelo slug (404 se não encontrado)."""
    return await catalog.get_by_slug(slug)
