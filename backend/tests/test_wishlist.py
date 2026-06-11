"""Testes da wishlist: adicionar, listar, remover, autenticação."""


async def _logar(client, email: str) -> dict:
    """Registra e loga um comprador; retorna o header de autorização."""
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "123456"}
    )
    login = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "123456"}
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def test_wishlist_add_listar_remover(client):
    """Adiciona, lista (idempotente) e remove um item da wishlist."""
    headers = await _logar(client, "wish@x.com")
    add = await client.post("/api/v1/wishlist/python-na-pratica", headers=headers)
    assert add.status_code == 204
    # idempotente
    await client.post("/api/v1/wishlist/python-na-pratica", headers=headers)

    lista = await client.get("/api/v1/wishlist", headers=headers)
    assert len(lista.json()) == 1

    await client.delete("/api/v1/wishlist/python-na-pratica", headers=headers)
    lista2 = await client.get("/api/v1/wishlist", headers=headers)
    assert len(lista2.json()) == 0


async def test_wishlist_sem_login_401(client):
    """Acessar a wishlist sem login retorna 401."""
    resposta = await client.get("/api/v1/wishlist")
    assert resposta.status_code == 401


async def test_wishlist_produto_inexistente_404(client):
    """Adicionar produto inexistente retorna 404."""
    headers = await _logar(client, "wish2@x.com")
    resposta = await client.post("/api/v1/wishlist/nao-existe", headers=headers)
    assert resposta.status_code == 404
