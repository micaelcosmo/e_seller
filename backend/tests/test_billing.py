"""Testes do perfil fiscal (billing_profile): upsert, validação e leitura."""


async def _registrar_logar(client, email: str) -> dict:
    """Registra e loga um usuário; retorna o header de autorização."""
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "123456"}
    )
    login = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "123456"}
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def test_criar_e_ler_perfil_fiscal(client):
    """Salvar o perfil fiscal e lê-lo de volta normaliza o documento."""
    headers = await _registrar_logar(client, "fiscal@x.com")
    payload = {
        "person_type": "individual",
        "legal_name": "Fulano de Tal",
        "document": "123.456.789-09",
        "city": "São Paulo",
        "state": "sp",
    }
    resp = await client.put("/api/v1/billing/profile", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["document"] == "12345678909"
    assert resp.json()["state"] == "SP"
    lido = await client.get("/api/v1/billing/profile", headers=headers)
    assert lido.status_code == 200
    assert lido.json()["legal_name"] == "Fulano de Tal"


async def test_upsert_idempotente(client):
    """Salvar duas vezes atualiza o mesmo perfil (não duplica)."""
    headers = await _registrar_logar(client, "fiscal2@x.com")
    base = {"legal_name": "A", "document": "11144477735"}
    await client.put("/api/v1/billing/profile", json=base, headers=headers)
    base["legal_name"] = "B"
    resp = await client.put("/api/v1/billing/profile", json=base, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["legal_name"] == "B"


async def test_documento_invalido_retorna_422(client):
    """CPF com tamanho incorreto é rejeitado (422)."""
    headers = await _registrar_logar(client, "fiscal3@x.com")
    payload = {"legal_name": "C", "document": "123"}
    resp = await client.put("/api/v1/billing/profile", json=payload, headers=headers)
    assert resp.status_code == 422


async def test_perfil_inexistente_retorna_404(client):
    """Ler perfil ainda não cadastrado retorna 404."""
    headers = await _registrar_logar(client, "fiscal4@x.com")
    resp = await client.get("/api/v1/billing/profile", headers=headers)
    assert resp.status_code == 404


async def test_exige_autenticacao(client):
    """Acesso sem token é negado (401)."""
    resp = await client.get("/api/v1/billing/profile")
    assert resp.status_code == 401
