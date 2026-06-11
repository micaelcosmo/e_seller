"""Testes BEQ-24: PATCH /api/v1/admin/coupons/{code} — editar cupom."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.coupons.models import Coupon, DiscountType
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


async def _make_coupon(db_session, code: str) -> Coupon:
    """Cria um cupom simples para edição."""
    coupon = Coupon(
        code=code,
        discount_type=DiscountType.PERCENT,
        value=10.0,
        active=True,
    )
    db_session.add(coupon)
    await db_session.commit()
    return coupon


async def test_edit_404_codigo_inexistente(client, db_session) -> None:
    """Código não encontrado retorna 404."""
    token = await _staff_token(client, db_session, "beq24_s1@x.com")
    resp = await client.patch(
        "/api/v1/admin/coupons/NAOEXISTE",
        json={"value": 20},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_edit_value(client, db_session) -> None:
    """Altera o valor do cupom."""
    await _make_coupon(db_session, "EDIT10A")
    token = await _staff_token(client, db_session, "beq24_s2@x.com")
    resp = await client.patch(
        "/api/v1/admin/coupons/EDIT10A",
        json={"value": 25},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert float(resp.json()["value"]) == 25.0


async def test_edit_max_redemptions(client, db_session) -> None:
    """Altera o limite de resgates."""
    await _make_coupon(db_session, "EDIT10B")
    token = await _staff_token(client, db_session, "beq24_s3@x.com")
    resp = await client.patch(
        "/api/v1/admin/coupons/EDIT10B",
        json={"max_redemptions": 50},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["max_redemptions"] == 50


async def test_edit_valid_until(client, db_session) -> None:
    """Altera a data de validade."""
    await _make_coupon(db_session, "EDIT10C")
    token = await _staff_token(client, db_session, "beq24_s4@x.com")
    until = "2027-12-31T23:59:59"
    resp = await client.patch(
        "/api/v1/admin/coupons/EDIT10C",
        json={"valid_until": until},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["valid_until"] is not None
