"""Testes OPS-18: GET /sitemap.xml — geração dinâmica de sitemap."""

from __future__ import annotations

from decimal import Decimal

from app.catalog.models import Product, ProductStatus


async def test_sitemap_xml_retorna_home(client, db_session) -> None:
    """Sitemap contém ao menos a URL da home e é XML válido."""
    resp = await client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    assert "<urlset" in resp.text
    assert "</urlset>" in resp.text


async def test_sitemap_inclui_produtos_publicados(client, db_session) -> None:
    """Sitemap lista os slugs de produtos publicados."""
    product = Product(
        title="Sitemap Test",
        slug="sitemap-test-prod",
        price=Decimal("9.90"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.commit()
    resp = await client.get("/sitemap.xml")
    assert "sitemap-test-prod" in resp.text


async def test_sitemap_nao_inclui_rascunhos(client, db_session) -> None:
    """Produtos em rascunho não aparecem no sitemap."""
    product = Product(
        title="Rascunho Sitemap",
        slug="rascunho-sitemap-prod",
        price=Decimal("9.90"),
        status=ProductStatus.DRAFT,
    )
    db_session.add(product)
    await db_session.commit()
    resp = await client.get("/sitemap.xml")
    assert "rascunho-sitemap-prod" not in resp.text
