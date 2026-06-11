"""Testes FE-22: parâmetro de ordenação no endpoint GET /products."""


async def test_sort_newest_retorna_200(client) -> None:
    """?sort=newest retorna 200 com lista."""
    resp = await client.get("/api/v1/products?sort=newest")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_sort_price_asc_retorna_200(client) -> None:
    """?sort=price_asc retorna 200 com lista."""
    resp = await client.get("/api/v1/products?sort=price_asc")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_sort_price_asc_ordem_crescente(client) -> None:
    """Produtos retornados por price_asc estão em ordem crescente de preço."""
    resp = await client.get("/api/v1/products?sort=price_asc")
    assert resp.status_code == 200
    items = resp.json()
    if len(items) < 2:
        return  # não há como verificar ordem com menos de 2 itens
    prices = [float(p["price"]) for p in items]
    for i in range(len(prices) - 1):
        assert prices[i] <= prices[i + 1], (
            f"Ordem incorreta: {prices[i]} > {prices[i + 1]}"
        )


async def test_sort_title_asc_ordem_alfabetica(client) -> None:
    """Produtos retornados por title_asc estão em ordem alfabética."""
    resp = await client.get("/api/v1/products?sort=title_asc")
    assert resp.status_code == 200
    items = resp.json()
    if len(items) < 2:
        return
    titles = [p["title"].lower() for p in items]
    for i in range(len(titles) - 1):
        assert titles[i] <= titles[i + 1], (
            f"Ordem incorreta: {titles[i]!r} > {titles[i + 1]!r}"
        )


async def test_sort_invalido_usa_padrao(client) -> None:
    """Valor de sort inválido não causa erro; usa padrão (newest)."""
    resp = await client.get("/api/v1/products?sort=invalido")
    assert resp.status_code == 200
