"""Testes de SEC-01: rate limiting nos endpoints críticos.

O _InMemoryStore é testado diretamente (lógica pura).
O teste de integração usa o `client` do conftest, que cria uma app isolada
com seu próprio `app.state.rate_store`.
"""

from app.core.rate_limit import _InMemoryStore


def test_requisicoes_dentro_do_limite_passam():
    """Até max_requests dentro da janela são permitidas."""
    store = _InMemoryStore()
    for _ in range(5):
        assert store.is_allowed("ip:rota", max_requests=5, window_seconds=60) is True


def test_requisicao_alem_do_limite_bloqueada():
    """A requisição que excede o limite é bloqueada."""
    store = _InMemoryStore()
    for _ in range(5):
        store.is_allowed("ip:rota", max_requests=5, window_seconds=60)
    assert store.is_allowed("ip:rota", max_requests=5, window_seconds=60) is False


def test_ips_distintos_sao_contados_separadamente():
    """Cada IP+rota tem sua própria janela."""
    store = _InMemoryStore()
    for _ in range(5):
        store.is_allowed("ip1:rota", max_requests=5, window_seconds=60)
    # ip1 está no limite; ip2 ainda não usou a rota
    assert store.is_allowed("ip1:rota", max_requests=5, window_seconds=60) is False
    assert store.is_allowed("ip2:rota", max_requests=5, window_seconds=60) is True


def test_janela_expirada_libera_requisicoes():
    """Após a janela expirar, o limite é resetado."""
    store = _InMemoryStore()
    import time
    now = time.monotonic()
    # Simula 5 requisições antigas (fora da janela de 1 segundo)
    for _ in range(5):
        store._windows.setdefault("ip:rota", __import__("collections").deque()).append(
            now - 2
        )
    # A janela de 1 segundo não cobre as requisições antigas
    assert store.is_allowed("ip:rota", max_requests=5, window_seconds=1) is True


async def test_login_retorna_429_apos_limite(client):
    """Após exceder o limite de login, retorna 429."""
    # O limite padrão é 10 por minuto; vamos simular 11 tentativas.
    for i in range(10):
        await client.post(
            "/api/v1/auth/token",
            data={"username": f"x{i}@x.com", "password": "pw"},
        )
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "last@x.com", "password": "pw"},
    )
    assert resp.status_code == 429
