"""Testes DOM-29: view_count incremental em GET /products/{slug} e relatório top-viewed."""  # noqa: E501

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


async def _make_product(db_session, slug: str, views: int = 0) -> Product:
    """Cria um produto publicado com view_count inicial."""
    product = Product(
        title=f"Livro {slug}",
        slug=slug,
        author="Autor",
        price=Decimal("29.90"),
        status=ProductStatus.PUBLISHED,
        view_count=views,
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def test_view_count_incrementa_ao_visitar(client, db_session) -> None:
    """GET /products/{slug} incrementa view_count a cada chamada."""
    await _make_product(db_session, "ebook-dom29-a", views=0)
    resp = await client.get("/api/v1/products/ebook-dom29-a")
    assert resp.status_code == 200
    assert resp.json()["view_count"] == 1
    resp2 = await client.get("/api/v1/products/ebook-dom29-a")
    assert resp2.json()["view_count"] == 2


async def test_view_count_nao_exposto_na_listagem(client, db_session) -> None:
    """GET /products (listagem) não expõe view_count."""
    await _make_product(db_session, "ebook-dom29-b")
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    assert "view_count" not in items[0]


async def test_top_viewed_retorna_ordenado(client, db_session) -> None:
    """GET /admin/products/top-viewed retorna os mais visualizados em ordem desc."""
    await _make_product(db_session, "ebook-dom29-c", views=5)
    await _make_product(db_session, "ebook-dom29-d", views=15)
    await _make_product(db_session, "ebook-dom29-e", views=8)
    token = await _staff_token(client, db_session, "dom29_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/products/top-viewed",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    slugs = [i["slug"] for i in items]
    assert slugs.index("ebook-dom29-d") < slugs.index("ebook-dom29-e")
    assert slugs.index("ebook-dom29-e") < slugs.index("ebook-dom29-c")
