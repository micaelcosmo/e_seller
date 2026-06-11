"""Testes BEQ-15: criação de cupom via POST /admin/coupons."""

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


async def test_criar_cupom_requer_auth(client) -> None:
    """POST /admin/coupons sem token retorna 401."""
    resp = await client.post(
        "/api/v1/admin/coupons",
        json={"code": "NOVO10", "discount_type": "percent", "value": "10"},
    )
    assert resp.status_code == 401


async def test_criar_cupom_percent_ok(client, db_session) -> None:
    """Staff cria cupom de desconto percentual com sucesso."""
    token = await _staff_token(client, db_session, "beq15_staff@x.com")
    resp = await client.post(
        "/api/v1/admin/coupons",
        json={"code": "BEQ15A", "discount_type": "percent", "value": "15"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "BEQ15A"
    assert data["discount_type"] == "percent"
    assert float(data["value"]) == 15.0
    assert data["active"] is True


async def test_criar_cupom_fixo_ok(client, db_session) -> None:
    """Staff cria cupom de desconto fixo com max_redemptions."""
    token = await _staff_token(client, db_session, "beq15_staff2@x.com")
    resp = await client.post(
        "/api/v1/admin/coupons",
        json={
            "code": "BEQ15B",
            "discount_type": "fixed",
            "value": "5.00",
            "max_redemptions": 100,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["max_redemptions"] == 100


async def test_codigo_duplicado_retorna_409(client, db_session) -> None:
    """Criar cupom com código já existente retorna 409."""
    from app.coupons.models import Coupon, DiscountType

    db_session.add(
        Coupon(code="DUPLO", discount_type=DiscountType.PERCENT, value=10, active=True)
    )
    await db_session.commit()
    token = await _staff_token(client, db_session, "beq15_staff3@x.com")
    resp = await client.post(
        "/api/v1/admin/coupons",
        json={"code": "duplo", "discount_type": "percent", "value": "10"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409


async def test_valor_negativo_retorna_422(client, db_session) -> None:
    """Valor de desconto negativo retorna 422."""
    token = await _staff_token(client, db_session, "beq15_staff4@x.com")
    resp = await client.post(
        "/api/v1/admin/coupons",
        json={"code": "NEGATIVO", "discount_type": "percent", "value": "-5"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
