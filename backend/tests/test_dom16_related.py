"""Testes DOM-16: endpoint de produtos relacionados."""


async def test_related_retorna_lista(client) -> None:
    """GET /products/{slug}/related retorna lista (pode ser vazia)."""
    resp = await client.get("/api/v1/products/python-na-pratica/related")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_related_nao_inclui_produto_proprio(client) -> None:
    """O produto consultado não aparece na lista de relacionados."""
    slug = "python-na-pratica"
    resp = await client.get(f"/api/v1/products/{slug}/related")
    assert resp.status_code == 200
    slugs = [p["slug"] for p in resp.json()]
    assert slug not in slugs, "O próprio produto apareceu nos relacionados."


async def test_related_produto_inexistente_retorna_lista_vazia(client) -> None:
    """Produto inexistente retorna lista vazia (sem 404)."""
    resp = await client.get("/api/v1/products/produto-que-nao-existe/related")
    assert resp.status_code == 200
    assert resp.json() == []
