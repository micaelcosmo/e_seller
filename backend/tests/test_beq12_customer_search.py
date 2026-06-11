"""Testes BEQ-12: pesquisa de clientes no painel admin."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_listagem_usuarios_requer_auth(client) -> None:
    """GET /admin/auth/users sem token retorna 401."""
    resp = await client.get("/api/v1/admin/auth/users")
    assert resp.status_code == 401


async def test_listagem_usuarios_staff_ok(client, db_session) -> None:
    """Staff obtém lista de clientes."""
    token = await _staff_token(client, db_session, "beq12_staff@x.com")
    resp = await client.get(
        "/api/v1/admin/auth/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) >= 1


async def test_busca_por_email_parcial(client, db_session) -> None:
    """Filtro ?q= retorna apenas clientes cujo e-mail contenha o termo."""
    hasher = PasswordHasher(iterations=1000)
    # Cria usuário com email único para facilitar a busca.
    db_session.add(
        User(
            email="unico_xyztest@cliente.com",
            password_hash=hasher.hash("pw"),
            role=UserRole.CUSTOMER,
        )
    )
    await db_session.commit()
    token = await _staff_token(client, db_session, "beq12_staff2@x.com")
    resp = await client.get(
        "/api/v1/admin/auth/users?q=xyztest",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    for item in items:
        assert "xyztest" in item["email"].lower(), (
            f"Item inesperado no resultado: {item['email']}"
        )


async def test_contas_anonimizadas_nao_aparecem(client, db_session) -> None:
    """Contas com deleted_at preenchido não aparecem na listagem."""
    from datetime import UTC, datetime

    hasher = PasswordHasher(iterations=1000)
    deleted_user = User(
        email="deletado_beq12@x.com",
        password_hash=hasher.hash("pw"),
        role=UserRole.CUSTOMER,
        deleted_at=datetime.now(UTC),
    )
    db_session.add(deleted_user)
    await db_session.commit()
    token = await _staff_token(client, db_session, "beq12_staff3@x.com")
    resp = await client.get(
        "/api/v1/admin/auth/users?q=deletado_beq12",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == [], "Conta anonimizada não deve aparecer na busca."
