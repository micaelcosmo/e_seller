"""Testes DOC-01: snapshot do contrato OpenAPI (contract testing)."""

from __future__ import annotations

import json


async def test_openapi_schema_retorna_200(client) -> None:
    """GET /openapi.json retorna 200 com objeto JSON válido."""
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema


async def test_openapi_tem_rotas_criticas(client) -> None:
    """O schema OpenAPI deve incluir as rotas críticas da API."""
    resp = await client.get("/openapi.json")
    paths = resp.json()["paths"]
    expected_routes = [
        "/api/v1/healthz",
        "/api/v1/auth/token",
        "/api/v1/auth/register",
        "/api/v1/products",
        "/api/v1/orders",
        "/api/v1/metrics",
        "/api/v1/dashboard",
    ]
    for route in expected_routes:
        assert route in paths, f"Rota ausente do schema: {route}"


async def test_openapi_versao_correta(client) -> None:
    """A versão da API no schema deve ser 0.2.0."""
    resp = await client.get("/openapi.json")
    info = resp.json()["info"]
    assert info["version"] == "0.2.0"
    assert "e_seller" in info["title"].lower()


async def test_openapi_snapshot_pode_ser_salvo(client, tmp_path) -> None:
    """Schema OpenAPI pode ser serializado e salvo em arquivo (snapshot)."""
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    snapshot_path = tmp_path / "openapi_snapshot.json"
    snapshot_path.write_text(
        json.dumps(resp.json(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    loaded = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert loaded["openapi"] == resp.json()["openapi"]
    assert len(loaded["paths"]) == len(resp.json()["paths"])
