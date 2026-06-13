"""Testes FEV: static files, design-system, toast.js servidos corretamente."""

import pytest


@pytest.mark.asyncio
async def test_design_system_css_served(client):
    """FEV-001: GET /static/css/design-system.css retorna 200 com Content-Type CSS."""
    resp = await client.get("/static/css/design-system.css")
    assert resp.status_code == 200
    assert "text/css" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_components_css_served(client):
    """FEV-002: GET /static/css/components.css retorna 200."""
    resp = await client.get("/static/css/components.css")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_toast_js_served(client):
    """FEV-003: GET /static/js/toast.js retorna 200."""
    resp = await client.get("/static/js/toast.js")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_router_js_served(client):
    """FEV-004: GET /static/js/router.js retorna 200."""
    resp = await client.get("/static/js/router.js")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_index_includes_design_system_link(client):
    """FEV-005: index.html inclui link para design-system.css."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "design-system.css" in resp.text


@pytest.mark.asyncio
async def test_index_includes_toast_script(client):
    """FEV-006: index.html inclui script toast.js."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "toast.js" in resp.text


@pytest.mark.asyncio
async def test_new_pages_render(client):
    """FEV-007: novas views /conta, /biblioteca, /carrinho, /favoritos retornam 200."""
    for path in ["/conta", "/biblioteca", "/carrinho", "/favoritos"]:
        resp = await client.get(path)
        assert resp.status_code == 200, f"Failed for {path}: {resp.status_code}"
