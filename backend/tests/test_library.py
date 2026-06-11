"""Testes de posse (entitlement) e 'Minha Biblioteca'."""


async def _registrar_e_logar(client, email: str) -> dict:
    """Registra e loga um comprador; retorna o header de autorização."""
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "123456"}
    )
    login = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "123456"}
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _comprar_e_pagar(client, headers: dict, slug: str) -> str:
    """Compra (logado) e aprova o pagamento; retorna a referência."""
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
            "provider_payment_id": f"lib-{reference}",
            "order_reference": reference,
            "provider_status": "approved",
        },
    )
    return reference


async def test_biblioteca_apos_compra_logada(client):
    """Após comprar logado e pagar, o e-book aparece na biblioteca."""
    headers = await _registrar_e_logar(client, "leitor@x.com")
    await _comprar_e_pagar(client, headers, "python-na-pratica")

    biblioteca = await client.get("/api/v1/library", headers=headers)
    assert biblioteca.status_code == 200
    itens = biblioteca.json()
    assert len(itens) == 1
    assert itens[0]["slug"] == "python-na-pratica"


async def test_reemissao_de_download_da_biblioteca(client):
    """O usuário reemite um link de download de um e-book possuído."""
    headers = await _registrar_e_logar(client, "leitor2@x.com")
    await _comprar_e_pagar(client, headers, "fastapi-do-zero")

    link = await client.post(
        "/api/v1/library/fastapi-do-zero/download-link", headers=headers
    )
    assert link.status_code == 200
    token = link.json()["token"]
    download = await client.get(f"/api/v1/download/{token}")
    assert download.status_code == 200


async def test_biblioteca_sem_login_retorna_401(client):
    """Acessar a biblioteca sem login retorna 401."""
    resposta = await client.get("/api/v1/library")
    assert resposta.status_code == 401


async def test_download_link_de_nao_possuido_retorna_403(client):
    """Reemitir link de um e-book que o usuário não possui retorna 403."""
    headers = await _registrar_e_logar(client, "leitor3@x.com")
    resposta = await client.post(
        "/api/v1/library/python-na-pratica/download-link", headers=headers
    )
    assert resposta.status_code == 403
