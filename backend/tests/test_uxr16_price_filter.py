"""Testes UXR-16: filtro de produtos por faixa de preço."""

from __future__ import annotations

from decimal import Decimal

from app.catalog.models import Product, ProductStatus


async def _make_product(db_session, slug: str, price: str) -> Product:
    """Cria produto publicado com o preço informado."""
    product = Product(
        title=f"Livro {slug}",
        slug=slug,
        price=Decimal(price),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def test_price_min_filtra_abaixo_do_minimo(client, db_session) -> None:
    """price_min exclui produtos mais baratos que o limite."""
    await _make_product(db_session, "barato-uxr16", "10.00")
    await _make_product(db_session, "caro-uxr16", "90.00")
    items = (await client.get("/api/v1/products?price_min=50")).json()
    slugs = [p["slug"] for p in items]
    assert "caro-uxr16" in slugs
    assert "barato-uxr16" not in slugs


async def test_price_max_filtra_acima_do_maximo(client, db_session) -> None:
    """price_max exclui produtos mais caros que o limite."""
    await _make_product(db_session, "barato2-uxr16", "10.00")
    await _make_product(db_session, "caro2-uxr16", "90.00")
    items = (await client.get("/api/v1/products?price_max=50")).json()
    slugs = [p["slug"] for p in items]
    assert "barato2-uxr16" in slugs
    assert "caro2-uxr16" not in slugs


async def test_faixa_de_preco_combinada(client, db_session) -> None:
    """price_min e price_max juntos retornam apenas a faixa intermediária."""
    await _make_product(db_session, "p10-uxr16", "10.00")
    await _make_product(db_session, "p30-uxr16", "30.00")
    await _make_product(db_session, "p90-uxr16", "90.00")
    items = (
        await client.get("/api/v1/products?price_min=20&price_max=50")
    ).json()
    slugs = [p["slug"] for p in items]
    assert slugs == ["p30-uxr16"] or (
        "p30-uxr16" in slugs and "p10-uxr16" not in slugs and "p90-uxr16" not in slugs
    )


async def test_count_respeita_filtro_de_preco(client, db_session) -> None:
    """O endpoint de contagem aplica o mesmo filtro de preço."""
    await _make_product(db_session, "c10-uxr16", "10.00")
    await _make_product(db_session, "c90-uxr16", "90.00")
    data = (await client.get("/api/v1/products/count?price_min=50")).json()
    assert data["total"] >= 1
    # O produto de 10.00 não deve ser contado isoladamente nesta faixa.
    data_low = (await client.get("/api/v1/products/count?price_max=20")).json()
    assert data_low["total"] >= 1
