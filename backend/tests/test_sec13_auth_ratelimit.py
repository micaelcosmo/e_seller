"""Testes SEC-13: AuthAwareRateLimit usa user_id em vez de IP para autenticados."""

from __future__ import annotations

from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.rate_limit import AuthAwareRateLimit, _InMemoryStore


def _build_app(max_requests: int, window_seconds: int) -> FastAPI:
    """Monta app mínima com um endpoint protegido por AuthAwareRateLimit."""
    app = FastAPI()
    app.state.rate_store = _InMemoryStore()
    limiter = AuthAwareRateLimit(
        max_requests=max_requests, window_seconds=window_seconds
    )

    @app.get("/test")
    def endpoint(_: None = Depends(limiter)) -> dict:
        """Endpoint de teste."""
        return {"ok": True}

    return app


async def _token(client: AsyncClient, email: str, password: str) -> str:
    """Faz login e retorna o access_token."""
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": password}
    )
    return resp.json()["access_token"]


async def test_anonimo_usa_ip(client, db_session) -> None:
    """Chave anônima usa ip: — não identifica por usuário."""
    store = _InMemoryStore()
    app = FastAPI()
    app.state.rate_store = store
    limiter = AuthAwareRateLimit(max_requests=2, window_seconds=60)

    @app.get("/t")
    def ep(_: None = Depends(limiter)) -> dict:
        """Endpoint de teste."""
        return {"ok": True}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r1 = await c.get("/t")
        r2 = await c.get("/t")
        r3 = await c.get("/t")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429


async def test_autenticado_usa_user_sub(client, db_session) -> None:
    """Usuário autenticado usa user:{email}:{path} como chave — não o IP."""
    from app.accounts.models import User, UserRole
    from app.security.passwords import PasswordHasher

    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="sec13@x.com",
            password_hash=hasher.hash("pw"),
            role=UserRole.CUSTOMER,
        )
    )
    await db_session.commit()
    token = await _token(client, "sec13@x.com", "pw")

    store = _InMemoryStore()
    app2 = FastAPI()
    app2.state.rate_store = store
    limiter = AuthAwareRateLimit(max_requests=2, window_seconds=60)

    @app2.get("/t")
    def ep(_: None = Depends(limiter)) -> dict:
        """Endpoint de teste."""
        return {"ok": True}

    transport = ASGITransport(app=app2)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        headers = {"Authorization": f"Bearer {token}"}
        r1 = await c.get("/t", headers=headers)
        r2 = await c.get("/t", headers=headers)
        r3 = await c.get("/t", headers=headers)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429


async def test_token_invalido_cai_em_ip(client, db_session) -> None:
    """Token inválido não dispara erro — cai para chave por IP."""
    store = _InMemoryStore()
    app3 = FastAPI()
    app3.state.rate_store = store
    limiter = AuthAwareRateLimit(max_requests=5, window_seconds=60)

    @app3.get("/t")
    def ep(_: None = Depends(limiter)) -> dict:
        """Endpoint de teste."""
        return {"ok": True}

    transport = ASGITransport(app=app3)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.get("/t", headers={"Authorization": "Bearer token_invalido"})
    assert resp.status_code == 200
