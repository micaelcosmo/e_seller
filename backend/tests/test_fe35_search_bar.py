"""Testes FE-35: barra de busca na vitrine (HTML + JS fetch)."""

from __future__ import annotations


async def test_home_contem_input_de_busca(client) -> None:
    """GET / deve renderizar um input de busca (id=search-input)."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert 'id="search-input"' in resp.text


async def test_home_contem_funcao_js_search(client) -> None:
    """Página inicial deve incluir a função JS searchProducts."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "searchProducts" in resp.text


async def test_home_js_chama_api_products(client) -> None:
    """Script de busca deve referenciar a rota /api/v1/products."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "/api/v1/products" in resp.text
