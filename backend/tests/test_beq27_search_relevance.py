"""Testes BEQ-27: relevância na busca por texto — título começa com query tem prioridade."""  # noqa: E501

from __future__ import annotations

from decimal import Decimal

from app.catalog.models import Product, ProductStatus


async def _make_product(db_session, slug: str, title: str) -> Product:
    """Cria produto publicado."""
    product = Product(
        title=title,
        slug=slug,
        price=Decimal("9.90"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def test_busca_retorna_resultados(client, db_session) -> None:
    """GET /products?q= retorna produtos que contenham o termo."""
    await _make_product(db_session, "python-beq27", "Python Básico")
    resp = await client.get("/api/v1/products?q=python")
    assert resp.status_code == 200
    assert any("beq27" in p["slug"] for p in resp.json())


async def test_relevancia_titulo_comeca_com_primeiro(client, db_session) -> None:
    """Produto cujo título começa com o termo vem antes do que contém no meio."""
    await _make_product(db_session, "fastapi-beq27", "FastAPI Avançado")
    await _make_product(db_session, "intro-beq27", "Intro ao FastAPI Moderno")
    resp = await client.get("/api/v1/products?q=fastapi")
    assert resp.status_code == 200
    items = resp.json()
    slugs = [p["slug"] for p in items]
    assert "fastapi-beq27" in slugs
    assert "intro-beq27" in slugs
    # "FastAPI Avançado" começa com "fastapi" → deve vir antes de "Intro ao FastAPI"
    assert slugs.index("fastapi-beq27") < slugs.index("intro-beq27")


async def test_busca_sem_resultados_retorna_lista_vazia(client, db_session) -> None:
    """Busca sem correspondência retorna lista vazia."""
    resp = await client.get("/api/v1/products?q=termoinexistente123xyz")
    assert resp.status_code == 200
    assert resp.json() == []
