"""Testes de cupons: validação, desconto no pedido e regras."""

from decimal import Decimal

from app.coupons.models import Coupon, DiscountType


async def _criar_cupom(
    db_session,
    code="OFF20",
    discount_type=DiscountType.PERCENT,
    value="20",
    active=True,
):
    """Cria um cupom no banco de teste."""
    coupon = Coupon(
        code=code,
        discount_type=discount_type,
        value=Decimal(value),
        active=active,
    )
    db_session.add(coupon)
    await db_session.commit()
    return coupon


async def test_validate_cupom_percentual(client, db_session):
    """Cupom de 20% sobre 100 retorna total 80 e desconto 20."""
    await _criar_cupom(db_session)
    resp = await client.post(
        "/api/v1/coupons/validate", json={"code": "OFF20", "amount": "100.00"}
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == "80.00"
    assert resp.json()["discount"] == "20.00"


async def test_validate_cupom_invalido_422(client):
    """Cupom inexistente retorna 422."""
    resp = await client.post(
        "/api/v1/coupons/validate", json={"code": "NAOEXISTE", "amount": "100.00"}
    )
    assert resp.status_code == 422


async def test_pedido_com_cupom_aplica_desconto(client, db_session):
    """Pedido com cupom de 20% reduz o valor (39.90 → 31.92)."""
    await _criar_cupom(db_session, code="OFF20", value="20")
    order = await client.post(
        "/api/v1/orders",
        json={
            "product_slug": "python-na-pratica",
            "buyer_email": "x@x.com",
            "coupon_code": "OFF20",
        },
    )
    assert order.status_code == 201
    assert order.json()["amount"] == "31.92"


async def test_pedido_com_cupom_invalido_422(client):
    """Pedido com cupom inválido retorna 422."""
    order = await client.post(
        "/api/v1/orders",
        json={
            "product_slug": "python-na-pratica",
            "buyer_email": "x@x.com",
            "coupon_code": "XX",
        },
    )
    assert order.status_code == 422


async def test_cupom_fixo_nao_fica_negativo(client, db_session):
    """Desconto fixo maior que o valor zera o total (nunca negativo)."""
    await _criar_cupom(
        db_session, code="MENOS100", discount_type=DiscountType.FIXED, value="100"
    )
    resp = await client.post(
        "/api/v1/coupons/validate", json={"code": "MENOS100", "amount": "39.90"}
    )
    assert resp.json()["total"] == "0.00"


async def test_cupom_inativo_422(client, db_session):
    """Cupom inativo é rejeitado."""
    await _criar_cupom(db_session, code="OFFOLD", value="10", active=False)
    resp = await client.post(
        "/api/v1/coupons/validate", json={"code": "OFFOLD", "amount": "50.00"}
    )
    assert resp.status_code == 422
