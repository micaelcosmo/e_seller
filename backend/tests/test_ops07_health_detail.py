"""Testes OPS-07: health check detalhado com diagnóstico de banco."""


async def test_healthz_basico(client) -> None:
    """GET /healthz retorna status ok (rápido, sem tocar no DB)."""
    resp = await client.get("/api/v1/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_healthz_detail_ok(client) -> None:
    """GET /healthz/detail retorna ok=True quando o banco está acessível."""
    resp = await client.get("/api/v1/healthz/detail")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert "checks" in data
    assert data["checks"]["database"]["ok"] is True


async def test_healthz_detail_checks_estrutura(client) -> None:
    """Resposta do healthz/detail contém campo checks com database."""
    resp = await client.get("/api/v1/healthz/detail")
    data = resp.json()
    assert "database" in data["checks"]
    assert "ok" in data["checks"]["database"]
