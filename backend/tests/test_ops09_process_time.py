"""Testes OPS-09: header X-Process-Time em todas as respostas."""


async def test_process_time_presente_em_resposta_ok(client) -> None:
    """GET /healthz inclui o header X-Process-Time."""
    resp = await client.get("/api/v1/healthz")
    assert resp.status_code == 200
    assert "x-process-time" in resp.headers, "Header X-Process-Time ausente."


async def test_process_time_e_numerico(client) -> None:
    """O valor do header X-Process-Time é um número de ponto flutuante."""
    resp = await client.get("/api/v1/healthz")
    value = resp.headers.get("x-process-time", "")
    try:
        parsed = float(value)
    except ValueError:
        raise AssertionError(f"X-Process-Time não é numérico: {value!r}") from None
    assert parsed >= 0, "X-Process-Time não pode ser negativo."


async def test_process_time_presente_em_404(client) -> None:
    """Mesmo rotas inexistentes retornam o header X-Process-Time."""
    resp = await client.get("/rota-que-nao-existe-404")
    assert "x-process-time" in resp.headers
