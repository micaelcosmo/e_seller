"""Testes do catálogo (listagem, detalhe, busca, publicação) — async."""


async def test_lista_apenas_produtos_publicados(client):
    """A vitrine retorna só publicados (o rascunho não aparece)."""
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    slugs = []
    for item in body:
        slugs.append(item["slug"])
    assert "rascunho-oculto" not in slugs


async def test_detalhe_de_produto_publicado(client):
    """O detalhe de um produto publicado retorna seus dados."""
    response = await client.get("/api/v1/products/python-na-pratica")
    assert response.status_code == 200
    assert response.json()["title"] == "Python na Prática"


async def test_detalhe_de_rascunho_retorna_404(client):
    """Um produto em rascunho não é acessível pelo detalhe público."""
    response = await client.get("/api/v1/products/rascunho-oculto")
    assert response.status_code == 404


async def test_busca_por_titulo(client):
    """A busca encontra produtos publicados por título."""
    response = await client.get("/api/v1/products", params={"q": "fastapi"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["slug"] == "fastapi-do-zero"


async def test_produto_nao_expoe_arquivo(client):
    """O schema de saída não revela o arquivo do e-book."""
    response = await client.get("/api/v1/products/python-na-pratica")
    assert "file_name" not in response.json()
