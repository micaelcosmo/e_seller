"""Testes FE-31: seção de destaque na página inicial do storefront."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import update

from app.catalog.models import Product, ProductStatus


async def _make_product(
    db_session,
    slug: str,
    title: str,
    featured: bool = False,
) -> Product:
    """Cria produto publicado."""
    product = Product(
        title=title,
        slug=slug,
        price=Decimal("19.90"),
        status=ProductStatus.PUBLISHED,
        featured=featured,
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def _clear_featured(db_session) -> None:
    """Zera o destaque de todos os produtos (inclui os vindos do seed dev).

    Garante o cenário 'sem destaque' de forma determinística, independente
    de o seed marcar algum produto como featured.
    """
    await db_session.execute(update(Product).values(featured=False))
    await db_session.commit()


async def test_home_sem_destaque_nao_exibe_secao(client, db_session) -> None:
    """Home sem produtos em destaque não exibe seção de destaque."""
    await _clear_featured(db_session)
    await _make_product(db_session, "comum-fe31", "Livro Comum")
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "Em Destaque" not in resp.text


async def test_home_com_destaque_exibe_secao(client, db_session) -> None:
    """Home com produto featured=True exibe seção 'Em Destaque'."""
    await _make_product(db_session, "dest-fe31", "Livro em Destaque", featured=True)
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "Em Destaque" in resp.text
    assert "Livro em Destaque" in resp.text


async def test_produto_destaque_aparece_com_borda_accent(client, db_session) -> None:
    """Produto em destaque tem classe de borda accent na seção de destaque."""
    await _make_product(db_session, "accent-fe31", "Python Pro", featured=True)
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "border-color:var(--accent)" in resp.text
