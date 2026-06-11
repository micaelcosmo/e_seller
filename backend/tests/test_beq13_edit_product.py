"""Testes BEQ-13: edição de produto via PATCH /admin/products/{slug}."""

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


async def test_edicao_requer_auth(client) -> None:
    """PATCH /admin/products/{slug} sem token retorna 401."""
    resp = await client.patch(
        "/api/v1/admin/products/python-na-pratica",
        json={"title": "Novo Título"},
    )
    assert resp.status_code == 401


async def test_editar_titulo_ok(client, db_session) -> None:
    """Staff pode editar o título do produto."""
    token = await _staff_token(client, db_session, "beq13_staff@x.com")
    resp = await client.patch(
        "/api/v1/admin/products/python-na-pratica",
        json={"title": "Python na Prática — Atualizado"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Python na Prática — Atualizado"


async def test_editar_preco_ok(client, db_session) -> None:
    """Staff pode alterar o preço do produto."""
    token = await _staff_token(client, db_session, "beq13_staff2@x.com")
    resp = await client.patch(
        "/api/v1/admin/products/python-na-pratica",
        json={"price": "99.90"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["price"]) == 99.90


async def test_editar_produto_inexistente_retorna_404(client, db_session) -> None:
    """PATCH em slug inexistente retorna 404."""
    token = await _staff_token(client, db_session, "beq13_staff3@x.com")
    resp = await client.patch(
        "/api/v1/admin/products/slug-que-nao-existe",
        json={"title": "Título"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


async def test_preco_negativo_retorna_422(client, db_session) -> None:
    """Preço negativo no corpo retorna 422."""
    token = await _staff_token(client, db_session, "beq13_staff4@x.com")
    resp = await client.patch(
        "/api/v1/admin/products/python-na-pratica",
        json={"price": "-10"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
