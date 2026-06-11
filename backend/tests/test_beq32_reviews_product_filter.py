"""Testes BEQ-32: filtro por product_id na listagem admin de avaliações."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.catalog.models import Product, ProductStatus
from app.reviews.models import Review
from app.security.passwords import PasswordHasher


async def _make_staff(db_session, email: str) -> str:
    """Cria conta staff e retorna email."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.flush()
    return email


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token JWT."""
    await _make_staff(db_session, email)
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


def _product(slug: str, title: str) -> Product:
    """Cria instância de Product com campos mínimos."""
    return Product(
        title=title,
        slug=slug,
        price=Decimal("10.00"),
        status=ProductStatus.PUBLISHED,
    )


async def test_filtra_reviews_por_product_id(client, db_session) -> None:
    """?product_id= deve retornar apenas avaliações do produto indicado."""
    buyer = User(
        email="beq32buyer@x.com",
        password_hash=PasswordHasher(iterations=1000).hash("pw"),
    )
    db_session.add(buyer)
    p1 = _product("produto-a-beq32", "Produto A")
    p2 = _product("produto-b-beq32", "Produto B")
    db_session.add_all([p1, p2])
    await db_session.flush()
    r1 = Review(product_id=p1.id, user_id=buyer.id, rating=4, comment="ok p1")
    r2 = Review(product_id=p2.id, user_id=buyer.id, rating=5, comment="ok p2")
    db_session.add_all([r1, r2])
    await db_session.commit()

    token = await _staff_token(client, db_session, "beq32staff@x.com")
    resp = await client.get(
        f"/api/v1/admin/reviews?product_id={p1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    for item in items:
        assert item["product_id"] == p1.id


async def test_sem_product_id_retorna_todos(client, db_session) -> None:
    """Sem ?product_id= a listagem retorna avaliações de todos os produtos."""
    buyer = User(
        email="beq32b_buyer@x.com",
        password_hash=PasswordHasher(iterations=1000).hash("pw"),
    )
    db_session.add(buyer)
    p1 = _product("prod-c-beq32", "Prod C")
    p2 = _product("prod-d-beq32", "Prod D")
    db_session.add_all([p1, p2])
    await db_session.flush()
    db_session.add_all([
        Review(product_id=p1.id, user_id=buyer.id, rating=3, comment="c"),
        Review(product_id=p2.id, user_id=buyer.id, rating=4, comment="d"),
    ])
    await db_session.commit()

    token = await _staff_token(client, db_session, "beq32b_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/reviews",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    product_ids = {item["product_id"] for item in resp.json()}
    assert len(product_ids) >= 2


async def test_x_total_count_com_product_filter(client, db_session) -> None:
    """X-Total-Count deve refletir apenas as reviews do produto filtrado."""
    buyer = User(
        email="beq32c_buyer@x.com",
        password_hash=PasswordHasher(iterations=1000).hash("pw"),
    )
    db_session.add(buyer)
    p = _product("prod-e-beq32", "Prod E")
    db_session.add(p)
    await db_session.flush()
    db_session.add(Review(product_id=p.id, user_id=buyer.id, rating=5, comment="e"))
    await db_session.commit()

    token = await _staff_token(client, db_session, "beq32c_staff@x.com")
    resp = await client.get(
        f"/api/v1/admin/reviews?product_id={p.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert int(resp.headers["x-total-count"]) == 1
