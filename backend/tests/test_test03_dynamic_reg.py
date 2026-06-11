"""Testes TEST-03: cadastro dinâmico de e-book (3 modos) + SSRF + upload."""

from __future__ import annotations

import io
import json
from unittest.mock import patch

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str = "staff3@x.com") -> str:
    """Cria staff e retorna o token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw123"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw123"}
    )
    return resp.json()["access_token"]


async def test_modo_manual_cria_produto(client, db_session) -> None:
    """Modo manual (POST /admin/products) cria produto com slug gerado."""
    token = await _staff_token(client, db_session)
    resp = await client.post(
        "/api/v1/admin/products",
        json={"title": "Manual Test", "price": "10.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Manual Test"
    assert "slug" in body and body["slug"]


async def test_modo_manual_titulo_vazio_retorna_422(client, db_session) -> None:
    """Cadastro com título vazio retorna 422 (validação Pydantic)."""
    token = await _staff_token(client, db_session, "staff3b@x.com")
    resp = await client.post(
        "/api/v1/admin/products",
        json={"title": "", "price": "10.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


async def test_modo_link_ssrf_bloqueado(client, db_session) -> None:
    """Import via URL local/privada deve ser bloqueado (anti-SSRF 422)."""
    token = await _staff_token(client, db_session, "staff3c@x.com")
    for url in ["http://localhost/manifest.json", "http://127.0.0.1/x"]:
        resp = await client.post(
            "/api/v1/admin/products/import",
            json={"url": url},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422, f"esperado 422 para {url}"


async def test_modo_link_importa_manifest(client, db_session) -> None:
    """Modo link: importa manifest de URL externa (HTTP mockado)."""
    token = await _staff_token(client, db_session, "staff3d@x.com")
    manifest = {"title": "E-book via Link", "price": "19.90"}
    with patch(
        "app.catalog.services.HttpManifestImporter._fetch_sync",
        return_value=json.dumps(manifest).encode(),
    ):
        resp = await client.post(
            "/api/v1/admin/products/import",
            json={"url": "https://example.com/manifest.json"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 201
    assert resp.json()["title"] == "E-book via Link"


async def test_upload_arquivo_pdf(client, db_session) -> None:
    """Upload de arquivo PDF cria ProductFile com formato correto."""
    token = await _staff_token(client, db_session, "staff3e@x.com")
    create = await client.post(
        "/api/v1/admin/products",
        json={"title": "Upload Test", "price": "5.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create.status_code == 201
    slug = create.json()["slug"]

    pdf_data = b"%PDF-1.4 fake content"
    resp = await client.post(
        f"/api/v1/admin/products/{slug}/upload-file",
        files={"file": ("livro.pdf", io.BytesIO(pdf_data), "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["file_format"] == "pdf"
    assert body["is_primary"] is True
    assert body["byte_size"] == len(pdf_data)


async def test_upload_formato_invalido_retorna_422(client, db_session) -> None:
    """Upload com extensão não suportada retorna 422."""
    token = await _staff_token(client, db_session, "staff3f@x.com")
    create = await client.post(
        "/api/v1/admin/products",
        json={"title": "Bad Format", "price": "5.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    slug = create.json()["slug"]
    resp = await client.post(
        f"/api/v1/admin/products/{slug}/upload-file",
        files={"file": ("doc.docx", io.BytesIO(b"x"), "application/octet-stream")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
