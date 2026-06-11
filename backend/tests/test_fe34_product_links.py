"""Testes FE-34: links para página de detalhes nos cards da vitrine."""

from __future__ import annotations

from decimal import Decimal

from app.catalog.models import Product, ProductStatus


async def _make_product(db_session, slug: str, title: str) -> Product:
    """Cria produto publicado para testes."""
    product = Product(
        title=title,
        slug=slug,
        price=Decimal("19.90"),
        status=ProductStatus.PUBLISHED,
        description="Descrição de teste.",
        author="Autor Teste",
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def test_card_contem_link_para_detalhe(client, db_session) -> None:
    """Card da vitrine deve conter link /produto/{slug} no título."""
    await _make_product(db_session, "livro-fe34", "Livro FE34 Teste")
    resp = await client.get("/")
    assert resp.status_code == 200
    assert 'href="/produto/livro-fe34"' in resp.text


async def test_card_destaque_contem_link_para_detalhe(client, db_session) -> None:
    """Card de destaque também deve conter link para a página de detalhes."""
    product = await _make_product(db_session, "destaque-fe34", "Destaque FE34")
    product.featured = True
    await db_session.commit()
    resp = await client.get("/")
    assert resp.status_code == 200
    assert 'href="/produto/destaque-fe34"' in resp.text


async def test_link_titulo_contem_nome_do_produto(client, db_session) -> None:
    """Âncora do link contém o título do produto para UX correta."""
    await _make_product(db_session, "ebook-fe34-nome", "eBook Nome FE34")
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "eBook Nome FE34" in resp.text
    assert "/produto/ebook-fe34-nome" in resp.text
