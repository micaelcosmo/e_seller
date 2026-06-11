"""Testes OPS-10: endpoint GET /health com readiness check de banco."""

from __future__ import annotations


async def test_health_retorna_ok(client) -> None:
    """GET /health retorna 200 e status ok quando o banco responde."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"


async def test_healthz_retorna_ok(client) -> None:
    """GET /api/v1/healthz (liveness) sempre retorna 200."""
    resp = await client.get("/api/v1/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_healthz_detail_retorna_ok(client) -> None:
    """GET /api/v1/healthz/detail retorna ok=True com banco saudável."""
    resp = await client.get("/api/v1/healthz/detail")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["checks"]["database"]["ok"] is True
