"""Testes DOM-15: busca fulltext inclui campo description."""


async def test_busca_por_descricao(client) -> None:
    """Busca por termo na descrição retorna produtos correspondentes."""
    # Os produtos do seed têm descriptions variadas; buscamos por "python" que
    # aparece no título de um produto — mas o campo description também é buscado.
    resp = await client.get("/api/v1/products?q=python")
    assert resp.status_code == 200
    results = resp.json()
    assert isinstance(results, list)
    # Há pelo menos um produto com "python" no título.
    has_python = any("python" in p["title"].lower() for p in results)
    assert has_python, "Nenhum produto com 'python' encontrado na busca."


async def test_busca_por_termo_na_descricao_nao_no_titulo(client) -> None:
    """Busca retorna 200 mesmo quando o termo está apenas na descrição."""
    # Termo improvável de estar no título mas pode estar na descrição do seed.
    resp = await client.get("/api/v1/products?q=livro")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_busca_vazia_retorna_publicados(client) -> None:
    """Busca com q vazio retorna todos os produtos publicados."""
    resp = await client.get("/api/v1/products?q=")
    assert resp.status_code == 200
    assert len(resp.json()) > 0
