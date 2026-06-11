"""Testes de AUTH-06: refresh token (renovação de sessão).

Cobre: login retorna refresh_token, /refresh emite novos tokens,
token inválido retorna 401, access token não funciona no /refresh.
"""


async def _register_and_login(client, email="u@x.com", password="pw1234"):
    """Auxilia: registra e faz login retornando o par de tokens."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
    )
    return resp.json()


async def test_login_retorna_refresh_token(client):
    """O login retorna access_token e refresh_token."""
    tokens = await _register_and_login(client)
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


async def test_refresh_emite_novos_tokens(client):
    """/refresh com token válido retorna novos access e refresh tokens bem formados."""
    tokens = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    # JWT tem 3 partes separadas por ponto.
    assert new_tokens["access_token"].count(".") == 2
    assert new_tokens["refresh_token"].count(".") == 2


async def test_refresh_token_invalido_retorna_401(client):
    """Token inválido (texto aleatório) retorna 401."""
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "nao.e.um.token"},
    )
    assert resp.status_code == 401


async def test_access_token_nao_vale_como_refresh(client):
    """O access token não pode ser usado no endpoint /refresh (401)."""
    tokens = await _register_and_login(client)
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )
    assert resp.status_code == 401


async def test_novo_access_token_autentica(client):
    """O access token obtido via /refresh permite chamar /me (200)."""
    tokens = await _register_and_login(client)
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    new_access = refresh_resp.json()["access_token"]
    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "u@x.com"
