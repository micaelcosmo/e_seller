"""Testes do cadastro dinâmico de e-book (manual/JSON/link) e autorização."""

import pytest

from app.accounts.models import User, UserRole
from app.catalog.services import (
    HttpManifestImporter,
    InvalidManifestUrl,
    ProductRegistrar,
)
from app.security.passwords import PasswordHasher


class _FakeImporter:
    """Importador de manifest falso (sem rede), para testes."""

    def __init__(self, payload: dict) -> None:
        """Guarda o payload a ser retornado."""
        self.payload = payload

    async def fetch_json(self, url: str) -> dict:
        """Retorna o payload fixo, ignorando a URL."""
        return self.payload


async def _admin_token(client, db_session) -> str:
    """Cria um admin no banco de teste e retorna um token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="boss@x.com",
            password_hash=hasher.hash("123456"),
            role=UserRole.ADMIN,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": "boss@x.com", "password": "123456"}
    )
    return resp.json()["access_token"]


async def test_cadastro_manual_admin(client, db_session):
    """Admin cadastra e-book pelo modo manual (201, rascunho com slug)."""
    token = await _admin_token(client, db_session)
    resp = await client.post(
        "/api/v1/admin/products",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Novo Livro", "author": "Autor", "price": "19.90"},
    )
    assert resp.status_code == 201
    assert resp.json()["slug"] == "novo-livro"


async def test_cadastro_sem_auth_retorna_401(client):
    """Sem token, o cadastro é negado (401)."""
    resp = await client.post(
        "/api/v1/admin/products", json={"title": "X", "price": "1.00"}
    )
    assert resp.status_code == 401


async def test_cadastro_customer_retorna_403(client):
    """Comprador (customer) não pode cadastrar (403)."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "c@x.com", "password": "123456"},
    )
    login = await client.post(
        "/api/v1/auth/token", data={"username": "c@x.com", "password": "123456"}
    )
    token = login.json()["access_token"]
    resp = await client.post(
        "/api/v1/admin/products",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "X", "price": "1.00"},
    )
    assert resp.status_code == 403


async def test_from_link_cria_rascunho(db_session):
    """O modo link importa um manifest (fake) e cria o rascunho."""
    importer = _FakeImporter({"title": "Importado", "author": "X", "price": "9.90"})
    registrar = ProductRegistrar(db_session, importer)
    product = await registrar.from_link("https://exemplo.com/manifest.json")
    assert product.slug == "importado"
    assert product.status.value == "draft"


async def test_from_json_invalido_levanta(db_session):
    """JSON sem preço é rejeitado na validação do schema."""
    registrar = ProductRegistrar(db_session, _FakeImporter({}))
    with pytest.raises(Exception):  # noqa: B017 - ValidationError do Pydantic
        await registrar.from_json({"title": "Sem preço"})


async def test_import_url_invalida_levanta():
    """URL não-http (ou local) é bloqueada (anti-SSRF)."""
    importer = HttpManifestImporter()
    with pytest.raises(InvalidManifestUrl):
        await importer.fetch_json("ftp://exemplo.com/x.json")
    with pytest.raises(InvalidManifestUrl):
        await importer.fetch_json("http://localhost/x.json")
