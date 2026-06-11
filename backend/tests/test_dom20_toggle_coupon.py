"""Testes DOM-20: toggle ativo/inativo de cupom via PATCH /admin/coupons/{code}/toggle."""  # noqa: E501

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.coupons.models import Coupon, DiscountType
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


async def _create_coupon(db_session, code: str, active: bool) -> Coupon:
    """Cria e persiste um cupom para os testes."""
    coupon = Coupon(
        code=code, discount_type=DiscountType.PERCENT, value=10, active=active
    )
    db_session.add(coupon)
    await db_session.commit()
    return coupon


async def test_toggle_requer_auth(client) -> None:
    """PATCH /admin/coupons/{code}/toggle sem token retorna 401."""
    resp = await client.patch("/api/v1/admin/coupons/ALGUM/toggle")
    assert resp.status_code == 401


async def test_toggle_ativa_cupom_inativo(client, db_session) -> None:
    """Toggle em cupom inativo o ativa."""
    await _create_coupon(db_session, "DOM20A", active=False)
    token = await _staff_token(client, db_session, "dom20_staff@x.com")
    resp = await client.patch(
        "/api/v1/admin/coupons/DOM20A/toggle",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["active"] is True


async def test_toggle_desativa_cupom_ativo(client, db_session) -> None:
    """Toggle em cupom ativo o desativa."""
    await _create_coupon(db_session, "DOM20B", active=True)
    token = await _staff_token(client, db_session, "dom20_staff2@x.com")
    resp = await client.patch(
        "/api/v1/admin/coupons/DOM20B/toggle",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["active"] is False


async def test_toggle_cupom_inexistente_retorna_404(client, db_session) -> None:
    """Toggle em código inexistente retorna 404."""
    token = await _staff_token(client, db_session, "dom20_staff3@x.com")
    resp = await client.patch(
        "/api/v1/admin/coupons/NAOEXISTE/toggle",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
