"""Testes DOM-19: listagem admin de cupons."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_listagem_cupons_requer_auth(client) -> None:
    """GET /admin/coupons sem token retorna 401."""
    resp = await client.get("/api/v1/admin/coupons")
    assert resp.status_code == 401


async def test_listagem_cupons_staff_ok(client, db_session) -> None:
    """Staff obtém lista de cupons."""
    from app.coupons.models import Coupon, DiscountType

    db_session.add(
        Coupon(code="TEST10", discount_type=DiscountType.PERCENT, value=10, active=True)
    )
    await db_session.commit()
    token = await _staff_token(client, db_session, "dom19_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/coupons",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    for item in items:
        assert "code" in item
        assert "discount_type" in item


async def test_filtro_only_active(client, db_session) -> None:
    """Filtro only_active=true retorna apenas cupons ativos."""
    from app.coupons.models import Coupon, DiscountType

    db_session.add(
        Coupon(
            code="INACTIVE5", discount_type=DiscountType.FIXED, value=5, active=False
        )
    )
    db_session.add(
        Coupon(
            code="ACTIVE20", discount_type=DiscountType.PERCENT, value=20, active=True
        )
    )
    await db_session.commit()
    token = await _staff_token(client, db_session, "dom19_staff2@x.com")
    resp = await client.get(
        "/api/v1/admin/coupons?only_active=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    for item in items:
        assert item["active"] is True, "Cupom inativo apareceu no filtro only_active."
