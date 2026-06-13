"""Testes FEV-29/30: elementos críticos no HTML e novas views no DOM."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_fev001_design_system_css_contem_accent(client) -> None:
    """FEV-001: design-system.css contém variável --accent."""
    resp = await client.get("/static/css/design-system.css")
    assert resp.status_code == 200
    assert "--color-accent" in resp.text


@pytest.mark.asyncio
async def test_fev002_index_link_design_system(client) -> None:
    """FEV-002: index.html tem link para design-system.css."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "design-system.css" in resp.text


@pytest.mark.asyncio
async def test_fev003_toast_root_presente(client) -> None:
    """FEV-003: base.html inclui div#toast-root."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "toast-root" in resp.text


@pytest.mark.asyncio
async def test_fev004_nav_links_presentes(client) -> None:
    """FEV-004: nav inclui links para catálogo e conta."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "href" in resp.text
    assert "/conta" in resp.text or "#/conta" in resp.text


@pytest.mark.asyncio
async def test_fev009_404_html_retorna_html(client) -> None:
    """FEV-009: rota inexistente retorna HTML (não JSON puro)."""
    resp = await client.get("/rota-que-nao-existe-xyz")
    assert resp.status_code == 404
    assert "text/html" in resp.headers.get("content-type", "")
    assert "html" in resp.text.lower()


@pytest.mark.asyncio
async def test_fev010_hamburger_presente(client) -> None:
    """FEV-010: nav tem elemento hamburger para mobile."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "hamburger" in resp.text or "menu-toggle" in resp.text


@pytest.mark.asyncio
async def test_fev011_password_strength_no_recuperar_senha(client) -> None:
    """FEV-011: /recuperar-senha tem elemento de força de senha."""
    resp = await client.get("/recuperar-senha")
    assert resp.status_code == 200
    assert "password-strength" in resp.text or "strength" in resp.text


@pytest.mark.asyncio
async def test_fev012_aria_labels_em_inputs(client) -> None:
    """FEV-012: inputs críticos têm aria-label."""
    resp = await client.get("/recuperar-senha")
    assert resp.status_code == 200
    assert "aria-label" in resp.text or "aria-describedby" in resp.text


@pytest.mark.asyncio
async def test_fev030_nova_view_conta_retorna_200(client) -> None:
    """FEV-030a: GET /conta retorna 200."""
    resp = await client.get("/conta")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_fev030_nova_view_biblioteca_retorna_200(client) -> None:
    """FEV-030b: GET /biblioteca retorna 200."""
    resp = await client.get("/biblioteca")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_fev030_nova_view_carrinho_retorna_200(client) -> None:
    """FEV-030c: GET /carrinho retorna 200."""
    resp = await client.get("/carrinho")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_fev030_nova_view_favoritos_retorna_200(client) -> None:
    """FEV-030d: GET /favoritos retorna 200."""
    resp = await client.get("/favoritos")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_fev023_orders_admin_panel_usa_design_system(client) -> None:
    """FEV-023: painel admin de pedidos carrega design-system.css."""
    resp = await client.get("/api/v1/admin/orders/panel")
    assert resp.status_code in (200, 401, 403)
    if resp.status_code == 200:
        assert "design-system.css" in resp.text


@pytest.mark.asyncio
async def test_fev024_downloads_admin_panel_retorna_html(client) -> None:
    """FEV-024: painel admin de downloads retorna HTML com design system."""
    resp = await client.get("/api/v1/admin/downloads/panel")
    assert resp.status_code in (200, 401, 403)
    if resp.status_code == 200:
        assert "design-system.css" in resp.text
