"""Testes ADM-10: fila de moderação de reviews pendentes."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.catalog.models import Product, ProductStatus
from app.core.config import get_settings
from app.reviews.models import Review, ReviewStatus
from app.security.jwt import JwtService
from app.security.passwords import PasswordHasher


async def _admin_token(db_session) -> str:
    """Cria usuário admin e retorna seu JWT."""
    settings = get_settings()
    hasher = PasswordHasher(settings.password_hash_iterations)
    user = User(
        email="admin_adm10@test.com",
        password_hash=hasher.hash("x"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return JwtService(secret_key=settings.app_secret_key).issue(user.email)


async def _seed(db_session) -> None:
    """Cria produto, dois usuários e reviews de diferentes status."""
    user1 = User(
        email="reviewer1_adm10@test.com",
        password_hash="x",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    user2 = User(
        email="reviewer2_adm10@test.com",
        password_hash="x",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    product = Product(
        title="Livro ADM10",
        slug="livro-adm10",
        price=Decimal("9.90"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(user1)
    db_session.add(user2)
    db_session.add(product)
    await db_session.commit()
    r1 = Review(
        product_id=product.id,
        user_id=user1.id,
        rating=5,
        comment="Pending",
        status=ReviewStatus.PENDING,
    )
    r2 = Review(
        product_id=product.id,
        user_id=user2.id,
        rating=4,
        comment="Approved",
        status=ReviewStatus.APPROVED,
    )
    db_session.add(r1)
    db_session.add(r2)
    await db_session.commit()


async def test_lista_reviews_admin_retorna_x_total_count(client, db_session) -> None:
    """GET /admin/reviews retorna header X-Total-Count."""
    token = await _admin_token(db_session)
    await _seed(db_session)
    resp = await client.get(
        "/api/v1/admin/reviews",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "x-total-count" in resp.headers
    assert int(resp.headers["x-total-count"]) >= 2


async def test_filtro_pending_retorna_apenas_pendentes(client, db_session) -> None:
    """GET /admin/reviews?status=pending retorna só reviews pendentes."""
    token = await _admin_token(db_session)
    await _seed(db_session)
    resp = await client.get(
        "/api/v1/admin/reviews?status=pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert all(r["status"] == "pending" for r in items)
    assert int(resp.headers["x-total-count"]) == len(items)


async def test_sem_autenticacao_retorna_401(client) -> None:
    """Endpoint admin requer autenticação."""
    resp = await client.get("/api/v1/admin/reviews")
    assert resp.status_code == 401
