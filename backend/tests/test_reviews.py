"""Testes de avaliações (review): comprador verificado, unicidade e nota."""


async def _registrar_logar(client, email: str) -> dict:
    """Registra e loga um comprador; retorna o header de autorização."""
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "123456"}
    )
    login = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "123456"}
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def _comprar_pagar(client, headers: dict, slug: str) -> None:
    """Compra (logado) e aprova o pagamento."""
    order = (
        await client.post(
            "/api/v1/orders",
            json={"product_slug": slug, "buyer_email": "x@x.com"},
            headers=headers,
        )
    ).json()
    reference = order["reference"]
    await client.post(
        "/api/v1/webhooks/mercadopago",
        json={
            "provider_payment_id": f"rev-{reference}",
            "order_reference": reference,
            "provider_status": "approved",
        },
    )


async def test_avaliar_como_comprador_pendente_e_listar(client):
    """Comprador verificado avalia (201); avaliação pendente não aparece na lista."""
    headers = await _registrar_logar(client, "rev@x.com")
    await _comprar_pagar(client, headers, "python-na-pratica")
    criar = await client.post(
        "/api/v1/products/python-na-pratica/reviews",
        headers=headers,
        json={"rating": 5, "comment": "Excelente!"},
    )
    assert criar.status_code == 201
    assert criar.json()["rating"] == 5
    assert criar.json()["id"] is not None

    # Avaliação pendente não aparece na lista pública (requer aprovação admin).
    lista = await client.get("/api/v1/products/python-na-pratica/reviews")
    assert lista.status_code == 200
    assert len(lista.json()) == 0


async def test_avaliar_sem_comprar_retorna_403(client):
    """Quem não comprou não pode avaliar (403)."""
    headers = await _registrar_logar(client, "rev2@x.com")
    resp = await client.post(
        "/api/v1/products/python-na-pratica/reviews",
        headers=headers,
        json={"rating": 4},
    )
    assert resp.status_code == 403


async def test_avaliar_duplicado_retorna_409(client):
    """Avaliar o mesmo e-book duas vezes retorna 409."""
    headers = await _registrar_logar(client, "rev3@x.com")
    await _comprar_pagar(client, headers, "fastapi-do-zero")
    await client.post(
        "/api/v1/products/fastapi-do-zero/reviews",
        headers=headers,
        json={"rating": 5},
    )
    segundo = await client.post(
        "/api/v1/products/fastapi-do-zero/reviews",
        headers=headers,
        json={"rating": 3},
    )
    assert segundo.status_code == 409


async def test_nota_invalida_retorna_422(client):
    """Nota fora de 1..5 é rejeitada (422)."""
    headers = await _registrar_logar(client, "rev4@x.com")
    await _comprar_pagar(client, headers, "arquitetura-limpa-web")
    resp = await client.post(
        "/api/v1/products/arquitetura-limpa-web/reviews",
        headers=headers,
        json={"rating": 9},
    )
    assert resp.status_code == 422


async def test_lista_reviews_publica_sem_login(client):
    """A lista de avaliações é pública (200 sem login)."""
    resp = await client.get("/api/v1/products/python-na-pratica/reviews")
    assert resp.status_code == 200
