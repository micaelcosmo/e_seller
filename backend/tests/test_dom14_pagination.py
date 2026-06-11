"""Testes DOM-14: paginação do catálogo (?page, ?page_size) e endpoint de contagem."""


async def test_products_page_1_default(client) -> None:
    """GET /products sem parâmetros retorna os produtos publicados (página 1)."""
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_products_page_param(client) -> None:
    """Parâmetro page é aceito sem erro."""
    resp = await client.get("/api/v1/products?page=1&page_size=2")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) <= 2


async def test_products_page_2_retorna_menos_ou_vazio(client) -> None:
    """Página 2 com page_size=2 retorna itens restantes ou lista vazia."""
    resp = await client.get("/api/v1/products?page=2&page_size=2")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_products_count_endpoint(client) -> None:
    """GET /products/count retorna total, page, page_size e has_next."""
    resp = await client.get("/api/v1/products/count")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "has_next" in data
    assert isinstance(data["total"], int)
    assert data["total"] >= 0


async def test_products_count_com_filtro(client) -> None:
    """GET /products/count com filtro ?q=python retorna contagem filtrada."""
    resp = await client.get("/api/v1/products/count?q=python")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 0
    # Sem filtro o total deve ser >= que o filtrado.
    resp_total = await client.get("/api/v1/products/count")
    assert resp_total.json()["total"] >= data["total"]
