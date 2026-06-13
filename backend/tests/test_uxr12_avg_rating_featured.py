"""Testes UXR-12/13: avg_rating e featured no ProductListItem.

Suportam o redesign dos cards (estrelas de avaliação e badge de destaque).
"""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.catalog.models import Product, ProductStatus
from app.reviews.models import Review, ReviewStatus


async def _make_product(
    db_session, slug: str, featured: bool = False
) -> Product:
    """Cria produto publicado, opcionalmente em destaque."""
    product = Product(
        title=f"Livro {slug}",
        slug=slug,
        price=Decimal("9.90"),
        status=ProductStatus.PUBLISHED,
        featured=featured,
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def _make_user(db_session, email: str) -> User:
    """Cria usuário de teste."""
    user = User(
        email=email, password_hash="x", role=UserRole.CUSTOMER, is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    return user


async def _approve_review(db_session, product, user, rating: int) -> None:
    """Cria uma review aprovada com a nota informada."""
    review = Review(
        product_id=product.id,
        user_id=user.id,
        rating=rating,
        comment="x",
        status=ReviewStatus.APPROVED,
    )
    db_session.add(review)
    await db_session.commit()


async def test_produto_sem_reviews_tem_avg_rating_zero(client, db_session) -> None:
    """Produto sem avaliações aprovadas tem avg_rating=0.0."""
    await _make_product(db_session, "sem-avg-uxr12")
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    target = next(
        (p for p in resp.json() if p["slug"] == "sem-avg-uxr12"), None
    )
    assert target is not None
    assert target["avg_rating"] == 0.0


async def test_avg_rating_e_media_das_notas_aprovadas(client, db_session) -> None:
    """avg_rating reflete a média (5 e 4 → 4.5) das reviews aprovadas."""
    product = await _make_product(db_session, "media-uxr12")
    u1 = await _make_user(db_session, "avg1uxr12@test.com")
    u2 = await _make_user(db_session, "avg2uxr12@test.com")
    await _approve_review(db_session, product, u1, 5)
    await _approve_review(db_session, product, u2, 4)
    resp = await client.get("/api/v1/products")
    target = next(
        (p for p in resp.json() if p["slug"] == "media-uxr12"), None
    )
    assert target is not None
    assert target["avg_rating"] == 4.5
    assert target["review_count"] == 2


async def test_featured_exposto_no_item(client, db_session) -> None:
    """O campo featured é exposto e reflete o valor do produto."""
    await _make_product(db_session, "destaque-uxr13", featured=True)
    await _make_product(db_session, "comum-uxr13", featured=False)
    items = (await client.get("/api/v1/products")).json()
    destaque = next((p for p in items if p["slug"] == "destaque-uxr13"), None)
    comum = next((p for p in items if p["slug"] == "comum-uxr13"), None)
    assert destaque is not None and destaque["featured"] is True
    assert comum is not None and comum["featured"] is False


async def test_filtro_featured_retorna_apenas_destaques(client, db_session) -> None:
    """O parâmetro featured=true lista apenas produtos em destaque (UXR-14)."""
    await _make_product(db_session, "feat-on-uxr14", featured=True)
    await _make_product(db_session, "feat-off-uxr14", featured=False)
    items = (await client.get("/api/v1/products?featured=true")).json()
    slugs = [p["slug"] for p in items]
    assert "feat-on-uxr14" in slugs
    assert "feat-off-uxr14" not in slugs
