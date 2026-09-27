"""Regressão QAF-06: cupom vale igual digitado em minúsculas ou com espaços.

Spec: `.spec/enrichment/roadmap-qaf.md` (QAF-06). A prévia da loja põe o código em
maiúsculas e diz "válido"; o pedido enviava o texto digitado e o backend comparava
exato — a tela prometia um desconto que o pedido recusava (422).
"""

from decimal import Decimal

from app.coupons.models import Coupon, DiscountType


async def _cupom(db_session) -> None:
    """Cupom de 10%, gravado em maiúsculas como a criação grava."""
    db_session.add(
        Coupon(
            code="QAF06",
            discount_type=DiscountType.PERCENT,
            value=Decimal("10"),
            active=True,
        )
    )
    await db_session.commit()


async def test_pedido_com_cupom_minusculo_aplica_o_desconto(client, db_session):
    """`qaf06` no pedido aplica os mesmos 10% que `QAF06`."""
    await _cupom(db_session)
    resposta = await client.post(
        "/api/v1/orders",
        json={
            "product_slug": "python-na-pratica",
            "buyer_email": "qa06@x.com",
            "coupon_code": "qaf06",
        },
    )
    assert resposta.status_code == 201
    assert resposta.json()["amount"] == "35.91"


async def test_validacao_com_espacos_e_minusculas_vale(client, db_session):
    """` qaf06 ` na validação responde válido com o total com desconto."""
    await _cupom(db_session)
    resposta = await client.post(
        "/api/v1/coupons/validate", json={"code": " qaf06 ", "amount": "39.90"}
    )
    assert resposta.status_code == 200
    assert resposta.json()["total"] == "35.91"
