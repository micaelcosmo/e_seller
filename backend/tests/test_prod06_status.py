"""Testes de PROD-06: toggle de status de publicação (admin).

Cobre: publicar rascunho, despublicar, status inválido (422), produto inexistente (404).
"""

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _admin_token(client, db_session) -> str:
    """Cria um admin no banco de teste e retorna token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="adm@x.com",
            password_hash=hasher.hash("pw1234"),
            role=UserRole.ADMIN,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": "adm@x.com", "password": "pw1234"}
    )
    return resp.json()["access_token"]


async def test_publicar_rascunho(client, db_session):
    """Admin publica o rascunho — status retorna 'published'."""
    token = await _admin_token(client, db_session)
    resp = await client.patch(
        "/api/v1/admin/products/rascunho-oculto/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "published"},
    )
    assert resp.status_code == 200
    assert resp.json()["slug"] == "rascunho-oculto"
    # Produto agora aparece na vitrine pública
    lista = await client.get("/api/v1/products")
    slugs = []
    for item in lista.json():
        slugs.append(item["slug"])
    assert "rascunho-oculto" in slugs


async def test_despublicar_produto(client, db_session):
    """Admin despublica um produto publicado — some da vitrine."""
    token = await _admin_token(client, db_session)
    resp = await client.patch(
        "/api/v1/admin/products/python-na-pratica/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "draft"},
    )
    assert resp.status_code == 200
    lista = await client.get("/api/v1/products")
    slugs = []
    for item in lista.json():
        slugs.append(item["slug"])
    assert "python-na-pratica" not in slugs


async def test_status_invalido_retorna_422(client, db_session):
    """Status desconhecido retorna 422."""
    token = await _admin_token(client, db_session)
    resp = await client.patch(
        "/api/v1/admin/products/python-na-pratica/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "pendente"},
    )
    assert resp.status_code == 422


async def test_produto_inexistente_retorna_404(client, db_session):
    """Produto com slug inexistente retorna 404."""
    token = await _admin_token(client, db_session)
    resp = await client.patch(
        "/api/v1/admin/products/nao-existe/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "published"},
    )
    assert resp.status_code == 404


async def test_sem_auth_retorna_401(client):
    """Sem token, o endpoint retorna 401."""
    resp = await client.patch(
        "/api/v1/admin/products/python-na-pratica/status",
        json={"status": "published"},
    )
    assert resp.status_code == 401
