"""Testes OPS-19: health check detalhado com versão e uptime."""

from __future__ import annotations


async def test_health_detail_retorna_campos_obrigatorios(client) -> None:
    """GET /health/detail retorna version, uptime_seconds, db_ok, storage_ok."""
    resp = await client.get("/health/detail")
    assert resp.status_code == 200
    data = resp.json()
    assert "version" in data
    assert "uptime_seconds" in data
    assert "db_ok" in data
    assert "storage_ok" in data


async def test_health_detail_db_ok_true(client) -> None:
    """GET /health/detail tem db_ok=True quando DB está acessível."""
    resp = await client.get("/health/detail")
    assert resp.status_code == 200
    assert resp.json()["db_ok"] is True


async def test_health_detail_version_nao_vazia(client) -> None:
    """GET /health/detail retorna versão não vazia."""
    resp = await client.get("/health/detail")
    assert resp.status_code == 200
    version = resp.json()["version"]
    assert isinstance(version, str)
    assert len(version) > 0
