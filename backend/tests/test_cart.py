"""Testes do carrinho: adicionar, listar, remover, checkout multi-item."""


async def _logar(client, email: str) -> dict:
    """Registra e loga um comprador; retorna o header de autorização."""
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "123456"}
    )
    login = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "123456"}
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def test_carrinho_add_listar_remover(client):
    """Adiciona dois itens, lista e remove um."""
    headers = await _logar(client, "cart@x.com")
    add = await client.post("/api/v1/cart/python-na-pratica", headers=headers)
    assert add.status_code == 204
    await client.post("/api/v1/cart/fastapi-do-zero", headers=headers)

    lista = await client.get("/api/v1/cart", headers=headers)
    assert len(lista.json()) == 2

    await client.delete("/api/v1/cart/python-na-pratica", headers=headers)
    lista2 = await client.get("/api/v1/cart", headers=headers)
    assert len(lista2.json()) == 1


async def test_carrinho_checkout_pedido_multi_item(client):
    """Checkout cria um pedido com todos os itens e esvazia o carrinho."""
    headers = await _logar(client, "cart2@x.com")
    await client.post("/api/v1/cart/python-na-pratica", headers=headers)
    await client.post("/api/v1/cart/fastapi-do-zero", headers=headers)

    order = await client.post("/api/v1/cart/checkout", headers=headers, json={})
    assert order.status_code == 201
    assert order.json()["amount"] == "89.80"

    lista = await client.get("/api/v1/cart", headers=headers)
    assert len(lista.json()) == 0


async def test_carrinho_checkout_vazio_400(client):
    """Checkout de carrinho vazio retorna 400."""
    headers = await _logar(client, "cart3@x.com")
    resposta = await client.post("/api/v1/cart/checkout", headers=headers, json={})
    assert resposta.status_code == 400


async def test_carrinho_sem_login_401(client):
    """Acessar o carrinho sem login retorna 401."""
    resposta = await client.get("/api/v1/cart")
    assert resposta.status_code == 401


async def test_carrinho_add_ja_possuido_409(client):
    """Adicionar um e-book já possuído retorna 409."""
    headers = await _logar(client, "cart4@x.com")
    order = (
        await client.post(
            "/api/v1/orders",
            json={"product_slug": "python-na-pratica", "buyer_email": "cart4@x.com"},
            headers=headers,
        )
    ).json()
    await client.post(
        "/api/v1/webhooks/mercadopago",
        json={
            "provider_payment_id": f"cart-{order['reference']}",
            "order_reference": order["reference"],
            "provider_status": "approved",
        },
    )
    resposta = await client.post("/api/v1/cart/python-na-pratica", headers=headers)
    assert resposta.status_code == 409
