"""Testes DOM-32: campo featured no catálogo — filtro GET /products?featured=true."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.catalog.models import Product, ProductStatus
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token JWT."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def _make_product(
    db_session, slug: str, featured: bool = False
) -> Product:
    """Cria produto publicado com featured configurado."""
    product = Product(
        title=f"Produto {slug}",
        slug=slug,
        price=Decimal("19.90"),
        status=ProductStatus.PUBLISHED,
        featured=featured,
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def test_filtro_featured_retorna_apenas_destaques(client, db_session) -> None:
    """GET /products?featured=true retorna somente produtos em destaque."""
    await _make_product(db_session, "destaque-dom32", featured=True)
    await _make_product(db_session, "normal-dom32", featured=False)
    resp = await client.get("/api/v1/products?featured=true")
    assert resp.status_code == 200
    slugs = [p["slug"] for p in resp.json()]
    assert "destaque-dom32" in slugs
    assert "normal-dom32" not in slugs


async def test_patch_produto_define_featured(client, db_session) -> None:
    """Admin pode marcar produto como destaque via PATCH /{slug}."""
    token = await _staff_token(client, db_session, "dom32_staff@x.com")
    product = await _make_product(db_session, "toggle-dom32", featured=False)
    resp = await client.patch(
        f"/api/v1/admin/products/{product.slug}",
        headers={"Authorization": f"Bearer {token}"},
        json={"featured": True},
    )
    assert resp.status_code == 200
    resp2 = await client.get("/api/v1/products?featured=true")
    slugs = [p["slug"] for p in resp2.json()]
    assert "toggle-dom32" in slugs


async def test_sem_filtro_retorna_todos(client, db_session) -> None:
    """GET /products sem featured retorna todos os publicados."""
    await _make_product(db_session, "feat-a-dom32", featured=True)
    await _make_product(db_session, "feat-b-dom32", featured=False)
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    slugs = [p["slug"] for p in resp.json()]
    assert "feat-a-dom32" in slugs
    assert "feat-b-dom32" in slugs
