"""Testes BEE: health check enriquecido com db_latency_ms e disk_free_mb."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_healthz_detail_inclui_latencia_db(client) -> None:
    """BEE-14a: GET /api/v1/healthz/detail inclui db_latency_ms no payload."""
    resp = await client.get("/api/v1/healthz/detail")
    assert resp.status_code == 200
    payload = resp.json()
    assert "checks" in payload
    assert "database" in payload["checks"]
    assert "latency_ms" in payload["checks"]["database"]
    assert payload["checks"]["database"]["latency_ms"] is not None


@pytest.mark.asyncio
async def test_healthz_detail_inclui_disco(client) -> None:
    """BEE-14b: GET /api/v1/healthz/detail inclui disk.free_mb."""
    resp = await client.get("/api/v1/healthz/detail")
    assert resp.status_code == 200
    payload = resp.json()
    assert "disk" in payload["checks"]
    assert "free_mb" in payload["checks"]["disk"]


@pytest.mark.asyncio
async def test_health_detail_inclui_latencia(client) -> None:
    """BEE-14c: GET /health/detail inclui db_latency_ms e disk_free_mb."""
    resp = await client.get("/health/detail")
    assert resp.status_code == 200
    payload = resp.json()
    assert "db_latency_ms" in payload
    assert "disk_free_mb" in payload


@pytest.mark.asyncio
async def test_problem_json_content_type(client) -> None:
    """BEE-15: exceção de domínio retorna Content-Type: application/problem+json."""
    resp = await client.get("/api/v1/products/slug-inexistente")
    assert resp.status_code == 404
    assert "application/problem+json" in resp.headers.get("content-type", "")
    body = resp.json()
    assert "type" in body
    assert "title" in body
    assert "status" in body
    assert "detail" in body
    assert body["status"] == 404
