"""Testes DBE: SearchService e endpoint /api/v1/search com fallback ILIKE."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import Product, ProductStatus
from app.catalog.search import SearchService


async def _add_product(db_session: AsyncSession, **kwargs) -> Product:
    """Adiciona um produto ao banco e retorna a instância persistida."""
    product = Product(**kwargs)
    db_session.add(product)
    await db_session.commit()
    return product


@pytest.mark.asyncio
async def test_search_returns_matching_title(db_session: AsyncSession) -> None:
    """DBE-04a: busca por palavra no título retorna produto correspondente.

    Usa o produto 'Python na Prática' semeado pelo DevSeeder.
    """
    service = SearchService(db_session)
    results = await service.search("Python")
    assert len(results) >= 1
    assert any("Python" in p.title for p in results)


@pytest.mark.asyncio
async def test_search_returns_matching_author(db_session: AsyncSession) -> None:
    """DBE-04b: busca por nome do autor retorna produto correspondente."""
    await _add_product(
        db_session,
        title="Livro Exclusivo do Autor",
        slug="dbe-test-author-exclusivo",
        author="Zeferino Particular",
        description="Conteúdo exclusivo para teste",
        price=1500,
        status=ProductStatus.PUBLISHED,
    )
    service = SearchService(db_session)
    results = await service.search("Zeferino")
    assert len(results) >= 1
    assert results[0].author == "Zeferino Particular"


@pytest.mark.asyncio
async def test_search_returns_matching_description(db_session: AsyncSession) -> None:
    """DBE-04c: busca por palavra na descrição retorna produto correspondente."""
    await _add_product(
        db_session,
        title="Guia de Orquestração",
        slug="dbe-test-orquestracao-xyz",
        author="Testador DBE",
        description="Abordagem de xylofonia aplicada a DevOps",
        price=1200,
        status=ProductStatus.PUBLISHED,
    )
    service = SearchService(db_session)
    results = await service.search("xylofonia")
    assert len(results) >= 1
    assert "xylofonia" in results[0].description.lower()


@pytest.mark.asyncio
async def test_search_excludes_draft(db_session: AsyncSession) -> None:
    """DBE-04d: produtos com status DRAFT não aparecem na busca.

    O DevSeeder já cria 'Rascunho (não publicado)' como draft.
    """
    service = SearchService(db_session)
    results = await service.search("Rascunho")
    assert all(p.status == ProductStatus.PUBLISHED for p in results)


@pytest.mark.asyncio
async def test_search_pagination(db_session: AsyncSession) -> None:
    """DBE-04e: paginação via skip/limit funciona corretamente."""
    service = SearchService(db_session)
    all_results = await service.search("a", skip=0, limit=100)
    assert len(all_results) >= 1
    if len(all_results) > 1:
        one_result = await service.search("a", skip=0, limit=1)
        assert len(one_result) == 1


@pytest.mark.asyncio
async def test_search_endpoint_returns_200(client) -> None:
    """DBE-04f: GET /api/v1/search?q=Python retorna 200 com lista JSON."""
    resp = await client.get("/api/v1/search?q=Python")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_search_endpoint_requires_min_length(client) -> None:
    """DBE-04g: GET /api/v1/search?q=a (1 char) retorna 422 — mínimo 2 chars."""
    resp = await client.get("/api/v1/search?q=a")
    assert resp.status_code == 422
