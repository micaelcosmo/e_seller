"""Regressão QAF-04/05: pedidos do admin com data; pendente com link de pagamento.

Spec: `.spec/enrichment/roadmap-qaf.md` (QAF-04 — US-07 pede status, valor e DATA;
QAF-05 — RF-25 pede retomar o pagamento de um pedido pendente).
"""

from __future__ import annotations

from decimal import Decimal

from app.accounts.models import User, UserRole
from app.orders.models import Order, OrderStatus
from app.security.passwords import PasswordHasher


async def _token(client, db_session, email: str, role: UserRole) -> tuple[str, int]:
    """Cria a conta e devolve (token, id do usuário)."""
    hasher = PasswordHasher(iterations=1000)
    usuario = User(email=email, password_hash=hasher.hash("pw"), role=role)
    db_session.add(usuario)
    await db_session.commit()
    resposta = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resposta.json()["access_token"], usuario.id


async def _pedido(db_session, user_id: int | None, status: OrderStatus) -> Order:
    """Pedido de 29.90 no status pedido."""
    pedido = Order(
        buyer_email="qa04@x.com",
        user_id=user_id,
        amount=Decimal("29.90"),
        status=status,
    )
    db_session.add(pedido)
    await db_session.commit()
    return pedido


async def test_lista_de_pedidos_do_admin_traz_data_e_email(client, db_session) -> None:
    """Cada item da lista do admin traz `created_at` e `buyer_email` (US-07)."""
    token, _ = await _token(client, db_session, "qa04-admin@x.com", UserRole.ADMIN)
    await _pedido(db_session, None, OrderStatus.PAID)
    resposta = await client.get(
        "/api/v1/orders", headers={"Authorization": f"Bearer {token}"}
    )
    assert resposta.status_code == 200
    itens = resposta.json()
    assert itens
    for item in itens:
        assert item["created_at"]
        assert item["buyer_email"] == "qa04@x.com"
        assert item["status"] == "paid"


async def test_pedido_pendente_em_meus_pedidos_traz_link_de_pagamento(
    client, db_session
) -> None:
    """Pendente volta com `checkout_url` para o simulador; pago volta sem (RF-25)."""
    token, user_id = await _token(
        client, db_session, "qa05-cliente@x.com", UserRole.CUSTOMER
    )
    pendente = await _pedido(db_session, user_id, OrderStatus.PENDING)
    pago = await _pedido(db_session, user_id, OrderStatus.PAID)
    resposta = await client.get(
        "/api/v1/orders/my", headers={"Authorization": f"Bearer {token}"}
    )
    assert resposta.status_code == 200
    por_referencia = {}
    for item in resposta.json():
        por_referencia[item["reference"]] = item
    assert por_referencia[pendente.reference]["checkout_url"].endswith(
        "/pay/simulate/" + pendente.reference
    )
    assert por_referencia[pago.reference]["checkout_url"] is None


async def test_pedido_pendente_por_referencia_traz_link_de_pagamento(
    client, db_session
) -> None:
    """A consulta pública do pedido pendente também oferece o link para pagar."""
    pendente = await _pedido(db_session, None, OrderStatus.PENDING)
    resposta = await client.get("/api/v1/orders/" + pendente.reference)
    assert resposta.status_code == 200
    assert resposta.json()["checkout_url"].endswith(
        "/pay/simulate/" + pendente.reference
    )
