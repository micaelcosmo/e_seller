"""Testes BEQ-26: PATCH /admin/reviews/{id}/moderate — moderação de avaliações."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.catalog.models import Product, ProductStatus
from app.reviews.models import Review, ReviewStatus
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


async def _make_review(db_session, rating: int = 4) -> Review:
    """Cria um produto e uma avaliação pendente."""
    from decimal import Decimal
    product = Product(
        title="Livro Mod",
        slug="livro-mod-beq26",
        price=Decimal("19.90"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.flush()
    user = User(email="beq26buyer@x.com", password_hash="x", role=UserRole.CUSTOMER)
    db_session.add(user)
    await db_session.flush()
    review = Review(
        product_id=product.id,
        user_id=user.id,
        rating=rating,
        comment="Ótimo!",
        status=ReviewStatus.PENDING,
    )
    db_session.add(review)
    await db_session.commit()
    return review


async def test_aprovar_review(client, db_session) -> None:
    """Admin aprova avaliação; status muda para approved."""
    token = await _staff_token(client, db_session, "beq26_s1@x.com")
    review = await _make_review(db_session)
    resp = await client.patch(
        f"/api/v1/admin/reviews/{review.id}/moderate",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "approved"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"


async def test_rejeitar_review(client, db_session) -> None:
    """Admin rejeita avaliação; status muda para rejected."""
    token = await _staff_token(client, db_session, "beq26_s2@x.com")
    review = await _make_review(db_session)
    resp = await client.patch(
        f"/api/v1/admin/reviews/{review.id}/moderate",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "rejected"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"


async def test_moderate_review_inexistente_retorna_404(client, db_session) -> None:
    """ID inexistente retorna 404."""
    token = await _staff_token(client, db_session, "beq26_s3@x.com")
    resp = await client.patch(
        "/api/v1/admin/reviews/99999/moderate",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "approved"},
    )
    assert resp.status_code == 404


async def test_moderate_status_invalido_retorna_422(client, db_session) -> None:
    """Status inválido retorna 422."""
    token = await _staff_token(client, db_session, "beq26_s4@x.com")
    review = await _make_review(db_session)
    resp = await client.patch(
        f"/api/v1/admin/reviews/{review.id}/moderate",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "invalido"},
    )
    assert resp.status_code == 422


async def test_review_aprovada_aparece_na_lista_publica(client, db_session) -> None:
    """Apenas avaliações aprovadas aparecem no GET /products/{slug}/reviews."""
    review = await _make_review(db_session)
    # Antes da aprovação: lista vazia.
    resp = await client.get("/api/v1/products/livro-mod-beq26/reviews")
    assert len(resp.json()) == 0
    # Aprovação via serviço direto.
    review.status = ReviewStatus.APPROVED
    await db_session.commit()
    # Após aprovação: avaliação aparece.
    resp = await client.get("/api/v1/products/livro-mod-beq26/reviews")
    assert len(resp.json()) == 1
    assert resp.json()[0]["comment"] == "Ótimo!"
