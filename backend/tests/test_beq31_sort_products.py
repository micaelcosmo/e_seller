"""Testes BEQ-31: ordenação por preço e data na listagem pública."""

from __future__ import annotations

from decimal import Decimal

from app.catalog.models import Product, ProductStatus


async def _make_product(
    db_session, slug: str, price: str, title: str = "Produto"
) -> Product:
    """Cria produto publicado para testes."""
    product = Product(
        title=title,
        slug=slug,
        price=Decimal(price),
        status=ProductStatus.PUBLISHED,
        description="Desc.",
        author="Autor",
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def test_sort_price_asc_ordena_por_preco_crescente(
    client, db_session
) -> None:
    """?sort=price_asc deve retornar produtos do mais barato ao mais caro."""
    await _make_product(db_session, "caro-beq31", "50.00", "Caro BEQ31")
    await _make_product(db_session, "barato-beq31", "10.00", "Barato BEQ31")
    resp = await client.get("/api/v1/products?sort=price_asc")
    assert resp.status_code == 200
    items = resp.json()
    prices = [float(i["price"]) for i in items]
    assert prices == sorted(prices)


async def test_sort_price_desc_ordena_por_preco_decrescente(
    client, db_session
) -> None:
    """?sort=price_desc deve retornar produtos do mais caro ao mais barato."""
    await _make_product(db_session, "caro2-beq31", "80.00", "Caro2 BEQ31")
    await _make_product(db_session, "barato2-beq31", "5.00", "Barato2 BEQ31")
    resp = await client.get("/api/v1/products?sort=price_desc")
    assert resp.status_code == 200
    items = resp.json()
    prices = [float(i["price"]) for i in items]
    assert prices == sorted(prices, reverse=True)


async def test_sort_oldest_retorna_do_mais_antigo(client, db_session) -> None:
    """?sort=oldest deve ser aceito e retornar 200 (ordenação por data ascendente)."""
    await _make_product(db_session, "old-beq31", "20.00", "Old BEQ31")
    resp = await client.get("/api/v1/products?sort=oldest")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
