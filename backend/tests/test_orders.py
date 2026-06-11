"""Testes de criação e consulta de pedidos — async."""


async def test_cria_pedido_pendente_com_checkout(client):
    """Criar pedido retorna 201, status pendente, valor e URL de checkout."""
    payload = {"product_slug": "python-na-pratica", "buyer_email": "leitor@exemplo.com"}
    response = await client.post("/api/v1/orders", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["amount"] == "39.90"
    assert body["checkout_url"]
    assert body["reference"]


async def test_email_invalido_retorna_422(client):
    """E-mail inválido é rejeitado pela validação (422)."""
    payload = {"product_slug": "python-na-pratica", "buyer_email": "nao-eh-email"}
    response = await client.post("/api/v1/orders", json=payload)
    assert response.status_code == 422


async def test_produto_inexistente_retorna_404(client):
    """Comprar um produto inexistente retorna 404."""
    payload = {"product_slug": "nao-existe", "buyer_email": "leitor@exemplo.com"}
    response = await client.post("/api/v1/orders", json=payload)
    assert response.status_code == 404


async def test_consulta_pedido_por_referencia(client):
    """Consultar um pedido criado retorna seu status."""
    payload = {"product_slug": "fastapi-do-zero", "buyer_email": "leitor@exemplo.com"}
    created = (await client.post("/api/v1/orders", json=payload)).json()
    response = await client.get(f"/api/v1/orders/{created['reference']}")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
