"""Testes FE-33: página de detalhes do produto no storefront."""

from __future__ import annotations

from decimal import Decimal

from app.catalog.models import Product, ProductStatus


async def _make_product(db_session, slug: str, title: str) -> Product:
    """Cria produto publicado."""
    product = Product(
        title=title,
        slug=slug,
        price=Decimal("24.90"),
        status=ProductStatus.PUBLISHED,
        description="Descrição do livro de teste.",
        author="Autor Teste",
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def test_pagina_produto_retorna_200(client, db_session) -> None:
    """GET /produto/{slug} retorna 200 para produto publicado."""
    await _make_product(db_session, "livro-fe33", "Livro FE33")
    resp = await client.get("/produto/livro-fe33")
    assert resp.status_code == 200
    assert "Livro FE33" in resp.text


async def test_pagina_produto_exibe_preco(client, db_session) -> None:
    """Página de detalhe exibe o preço do produto."""
    await _make_product(db_session, "preco-fe33", "Produto com Preço")
    resp = await client.get("/produto/preco-fe33")
    assert resp.status_code == 200
    assert "24,90" in resp.text or "24.90" in resp.text


async def test_pagina_produto_inexistente_retorna_404(client) -> None:
    """GET /produto/nao-existe retorna 404."""
    resp = await client.get("/produto/nao-existe-fe33")
    assert resp.status_code == 404
