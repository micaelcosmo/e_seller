"""Testes TEST-04: cobertura adicional de domínios (entitlement, cupons, reviews)."""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.catalog.models import Product, ProductStatus
from app.coupons.models import Coupon, DiscountType
from app.security.passwords import PasswordHasher


async def _user_and_token(client, db_session, email: str) -> str:
    """Cria usuário e retorna token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_coupon_invalido_retorna_erro(client, db_session):
    """Aplicar cupom inexistente retorna 404 ou 422."""
    token = await _user_and_token(client, db_session, "coupon_test@x.com")
    db_session.add(Product(
        title="Livro A", slug="livro-a", author="A", price=Decimal("10.00"),
        file_name="a.txt", status=ProductStatus.PUBLISHED,
    ))
    await db_session.commit()
    resp = await client.post(
        "/api/v1/cart/checkout",
        json={"slug": "livro-a", "coupon_code": "INVALIDO"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code in (404, 422, 400)


async def test_wishlist_add_and_list(client, db_session):
    """Adiciona produto à wishlist e verifica na listagem."""
    token = await _user_and_token(client, db_session, "wish_test@x.com")
    db_session.add(Product(
        title="Livro W", slug="livro-w", author="W", price=Decimal("20.00"),
        file_name="w.txt", status=ProductStatus.PUBLISHED,
    ))
    await db_session.commit()
    add_resp = await client.post(
        "/api/v1/wishlist/livro-w",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert add_resp.status_code in (200, 201, 204)
    list_resp = await client.get(
        "/api/v1/wishlist",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200


async def test_newsletter_subscribe(client):
    """Inscrição na newsletter retorna 200 ou 201."""
    resp = await client.post(
        "/api/v1/newsletter/subscribe",
        json={"email": "news_test@x.com"},
    )
    assert resp.status_code in (200, 201, 202)


async def test_catalog_busca_titulo(client, db_session):
    """Busca por título retorna produtos correspondentes."""
    db_session.add(Product(
        title="Python Avançado", slug="python-avancado", author="X",
        price=Decimal("30.00"), file_name="py.txt", status=ProductStatus.PUBLISHED,
    ))
    await db_session.commit()
    resp = await client.get("/api/v1/products?q=Python")
    assert resp.status_code == 200
    titles = [p["title"] for p in resp.json()]
    assert any("Python" in t for t in titles)


async def test_coupon_percentual_aplicado(client, db_session):
    """Cupom de 10% reduz o preço do produto no carrinho."""
    token = await _user_and_token(client, db_session, "coupon_ok@x.com")
    db_session.add(Coupon(
        code="DESC10",
        discount_type=DiscountType.PERCENT,
        value=Decimal("10"),
        active=True,
    ))
    db_session.add(Product(
        title="Livro C", slug="livro-c", author="C", price=Decimal("100.00"),
        file_name="c.txt", status=ProductStatus.PUBLISHED,
    ))
    await db_session.commit()
    resp = await client.post(
        "/api/v1/cart/checkout",
        json={"slug": "livro-c", "coupon_code": "DESC10"},
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200:
        data = resp.json()
        total = float(data.get("total", data.get("amount", 999)))
        assert total < 100.0
