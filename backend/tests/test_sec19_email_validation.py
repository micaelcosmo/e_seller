"""Testes SEC-19: validação de formato de e-mail no registro."""

from __future__ import annotations


async def test_registro_email_valido_retorna_201(client) -> None:
    """POST /register com e-mail válido deve retornar 201."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "usuario@exemplo.com", "password": "senha123"},
    )
    assert resp.status_code == 201


async def test_registro_email_invalido_retorna_422(client) -> None:
    """POST /register com e-mail sem @ deve retornar 422."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "nao-e-um-email", "password": "senha123"},
    )
    assert resp.status_code == 422


async def test_registro_email_sem_dominio_retorna_422(client) -> None:
    """POST /register com e-mail sem domínio válido deve retornar 422."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "usuario@", "password": "senha123"},
    )
    assert resp.status_code == 422


async def test_registro_email_normalizado_para_lowercase(client) -> None:
    """E-mail deve ser normalizado para lowercase no registro."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "USUARIO@EXEMPLO.COM", "password": "senha123"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "usuario@exemplo.com"
