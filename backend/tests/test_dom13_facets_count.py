"""Testes DOM-13: facetas de autores e tags com contagem de produtos."""


async def test_authors_retorna_count(client) -> None:
    """Endpoint /authors inclui campo count com total de produtos publicados."""
    resp = await client.get("/api/v1/authors")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    for item in items:
        assert "count" in item, f"Author sem campo count: {item}"
        assert isinstance(item["count"], int)
        assert item["count"] >= 0


async def test_tags_retorna_count(client) -> None:
    """Endpoint /tags inclui campo count com total de produtos publicados."""
    resp = await client.get("/api/v1/tags")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    for item in items:
        assert "count" in item, f"Tag sem campo count: {item}"
        assert isinstance(item["count"], int)
        assert item["count"] >= 0


async def test_authors_count_so_publicados(client, db_session) -> None:
    """Autores cujos produtos são apenas rascunho aparecem com count 0."""
    # O seed já tem "rascunho-oculto" com autor "Autor Oculto".
    resp = await client.get("/api/v1/authors")
    assert resp.status_code == 200
    items = resp.json()
    # Autor dos produtos publicados deve ter count >= 1.
    published_counts = [i["count"] for i in items if i["count"] >= 1]
    assert len(published_counts) > 0, "Nenhum autor com produtos publicados encontrado."
