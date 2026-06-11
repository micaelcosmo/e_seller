"""Testes SEC-07: headers de segurança HTTP (CSP, X-Frame-Options etc.)."""


async def test_csp_header_presente(client) -> None:
    """Todas as respostas incluem o header Content-Security-Policy."""
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    assert "content-security-policy" in resp.headers, (
        "Header Content-Security-Policy ausente na resposta."
    )


async def test_csp_contem_default_src_self(client) -> None:
    """O CSP padrão inclui 'default-src self'."""
    resp = await client.get("/api/v1/products")
    csp = resp.headers.get("content-security-policy", "")
    assert "default-src" in csp and "'self'" in csp


async def test_x_frame_options_deny(client) -> None:
    """Respostas incluem X-Frame-Options: DENY."""
    resp = await client.get("/api/v1/products")
    assert resp.headers.get("x-frame-options") == "DENY"


async def test_x_content_type_options_nosniff(client) -> None:
    """Respostas incluem X-Content-Type-Options: nosniff."""
    resp = await client.get("/api/v1/products")
    assert resp.headers.get("x-content-type-options") == "nosniff"
