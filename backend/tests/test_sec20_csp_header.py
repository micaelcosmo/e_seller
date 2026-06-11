"""Testes SEC-20: header Content-Security-Policy em respostas HTML."""

from __future__ import annotations


async def test_home_tem_csp_header(client) -> None:
    """GET / deve incluir header Content-Security-Policy."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "content-security-policy" in resp.headers


async def test_csp_inclui_default_src_self(client) -> None:
    """CSP deve incluir 'default-src' com restrição a 'self'."""
    resp = await client.get("/")
    csp = resp.headers.get("content-security-policy", "")
    assert "default-src" in csp
    assert "'self'" in csp


async def test_api_response_tem_csp_header(client) -> None:
    """Resposta da API também deve incluir CSP (middleware é global)."""
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    assert "content-security-policy" in resp.headers
