"""Testes de FE-13: filtro por tag e por autor na listagem de produtos.

Slug dos dados de seed:
  - Tag "fastapi"  → apenas FastAPI do Zero
  - Tag "python"   → Python na Prática e FastAPI do Zero (2 resultados)
  - Tag "solid"    → apenas Arquitetura Limpa na Web
  - Author "equipe-e-seller" → todos os 3 publicados
"""


async def test_filtro_por_tag_retorna_apenas_correspondentes(client):
    """?tag=fastapi retorna somente o produto com aquela tag."""
    response = await client.get("/api/v1/products", params={"tag": "fastapi"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["slug"] == "fastapi-do-zero"


async def test_filtro_por_tag_com_multiplos_resultados(client):
    """?tag=python retorna todos os produtos que têm a tag."""
    response = await client.get("/api/v1/products", params={"tag": "python"})
    assert response.status_code == 200
    body = response.json()
    slugs = []
    for item in body:
        slugs.append(item["slug"])
    assert "python-na-pratica" in slugs
    assert "fastapi-do-zero" in slugs
    assert "rascunho-oculto" not in slugs


async def test_filtro_por_tag_inexistente_retorna_lista_vazia(client):
    """?tag desconhecido retorna lista vazia (sem erro)."""
    response = await client.get("/api/v1/products", params={"tag": "nao-existe"})
    assert response.status_code == 200
    assert response.json() == []


async def test_filtro_por_autor_retorna_todos_publicados(client):
    """?author=equipe-e-seller retorna todos os produtos publicados daquele autor."""
    response = await client.get(
        "/api/v1/products", params={"author": "equipe-e-seller"}
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3


async def test_filtro_por_autor_inexistente_retorna_lista_vazia(client):
    """?author desconhecido retorna lista vazia (sem erro)."""
    response = await client.get(
        "/api/v1/products", params={"author": "autor-inexistente"}
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_filtro_por_tag_nao_retorna_rascunho(client):
    """Mesmo com tag válida, rascunhos não aparecem na listagem pública."""
    response = await client.get("/api/v1/products", params={"tag": "python"})
    assert response.status_code == 200
    for item in response.json():
        assert item["slug"] != "rascunho-oculto"


async def test_combinacao_tag_e_busca(client):
    """?q= e ?tag= podem ser combinados (retorna interseção)."""
    response = await client.get(
        "/api/v1/products", params={"q": "fastapi", "tag": "python"}
    )
    assert response.status_code == 200
    body = response.json()
    # FastAPI do Zero tem tag "python" e título contém "fastapi"
    assert len(body) == 1
    assert body[0]["slug"] == "fastapi-do-zero"
