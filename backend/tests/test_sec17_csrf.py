"""Testes SEC-17: middleware CSRF para formulários HTML."""

from __future__ import annotations


async def test_get_index_define_cookie_csrf(client) -> None:
    """GET / deve definir o cookie csrftoken na resposta."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "csrftoken" in resp.cookies


async def test_post_web_sem_token_retorna_403(client) -> None:
    """POST /comprar sem token CSRF retorna 403."""
    resp = await client.post(
        "/comprar",
        data={"slug": "qualquer", "email": "x@x.com"},
    )
    assert resp.status_code == 403


async def test_post_web_com_token_valido_nao_retorna_403(client) -> None:
    """POST /comprar com token CSRF correto não retorna 403."""
    get_resp = await client.get("/")
    csrf_token = get_resp.cookies.get("csrftoken", "")
    assert csrf_token, "Cookie csrftoken deve existir após GET"
    resp = await client.post(
        "/comprar",
        data={"slug": "nao-existe-sec17", "email": "x@x.com", "csrf_token": csrf_token},
        cookies={"csrftoken": csrf_token},
    )
    assert resp.status_code != 403


async def test_api_routes_isentas_de_csrf(client) -> None:
    """POST /api/v1/auth/token não exige token CSRF (rota de API é isenta)."""
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "naoexiste@sec17.com", "password": "qualquer"},
    )
    assert resp.status_code != 403
