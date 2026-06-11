"""Testes DOM-34: review_count nos produtos (sem N+1)."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.catalog.models import Product, ProductStatus
from app.reviews.models import Review, ReviewStatus


async def _make_product(db_session, slug: str) -> Product:
    """Cria produto publicado."""
    product = Product(
        title=f"Livro {slug}",
        slug=slug,
        price=Decimal("9.90"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.commit()
    return product


async def _make_user(db_session, email: str) -> User:
    """Cria usuário de teste."""
    user = User(email=email, password_hash="x", role=UserRole.CUSTOMER, is_active=True)
    db_session.add(user)
    await db_session.commit()
    return user


async def test_produto_sem_reviews_tem_review_count_zero(client, db_session) -> None:
    """Produto sem avaliações aprovadas tem review_count=0."""
    await _make_product(db_session, "sem-reviews-dom34")
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    items = resp.json()
    target = next((p for p in items if p["slug"] == "sem-reviews-dom34"), None)
    assert target is not None
    assert target["review_count"] == 0


async def test_produto_com_review_aprovada_tem_count_correto(client, db_session) -> None:  # noqa: E501
    """Produto com 2 reviews aprovadas retorna review_count=2."""
    product = await _make_product(db_session, "dois-reviews-dom34")
    u1 = await _make_user(db_session, "u1dom34@test.com")
    u2 = await _make_user(db_session, "u2dom34@test.com")
    r1 = Review(
        product_id=product.id,
        user_id=u1.id,
        rating=5,
        comment="Ótimo",
        status=ReviewStatus.APPROVED,
    )
    r2 = Review(
        product_id=product.id,
        user_id=u2.id,
        rating=4,
        comment="Bom",
        status=ReviewStatus.APPROVED,
    )
    db_session.add(r1)
    db_session.add(r2)
    await db_session.commit()
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    items = resp.json()
    target = next((p for p in items if p["slug"] == "dois-reviews-dom34"), None)
    assert target is not None
    assert target["review_count"] == 2


async def test_reviews_pendentes_nao_contam(client, db_session) -> None:
    """Reviews com status PENDING não são contadas no review_count."""
    product = await _make_product(db_session, "pendente-dom34")
    u1 = await _make_user(db_session, "pending1dom34@test.com")
    r_pending = Review(
        product_id=product.id,
        user_id=u1.id,
        rating=3,
        comment="Aguardando",
        status=ReviewStatus.PENDING,
    )
    db_session.add(r_pending)
    await db_session.commit()
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    items = resp.json()
    target = next((p for p in items if p["slug"] == "pendente-dom34"), None)
    assert target is not None
    assert target["review_count"] == 0
