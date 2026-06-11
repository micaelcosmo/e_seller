"""Testes OPS-08: endpoint /metrics/prometheus (formato Prometheus text)."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token de acesso."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_prometheus_requer_auth(client) -> None:
    """GET /metrics/prometheus sem token retorna 401."""
    resp = await client.get("/api/v1/metrics/prometheus")
    assert resp.status_code == 401


async def test_prometheus_retorna_texto(client, db_session) -> None:
    """Staff obtém resposta em formato text/plain Prometheus."""
    token = await _staff_token(client, db_session, "ops8_staff@x.com")
    resp = await client.get(
        "/api/v1/metrics/prometheus",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]


async def test_prometheus_contem_metricas_esperadas(client, db_session) -> None:
    """O texto Prometheus contém as métricas fundamentais."""
    token = await _staff_token(client, db_session, "ops8_staff2@x.com")
    resp = await client.get(
        "/api/v1/metrics/prometheus",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.text
    assert "eseller_products_total" in body
    assert "eseller_orders_total" in body
    assert "eseller_revenue_total_brl" in body


async def test_prometheus_formato_correto(client, db_session) -> None:
    """Cada linha de valor é do formato 'nome valor'."""
    token = await _staff_token(client, db_session, "ops8_staff3@x.com")
    resp = await client.get(
        "/api/v1/metrics/prometheus",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = resp.text
    for line in body.strip().splitlines():
        if line.startswith("#"):
            continue
        parts = line.split(" ")
        assert len(parts) == 2, f"Linha mal formatada: {line!r}"
        # O valor deve ser numérico.
        try:
            float(parts[1])
        except ValueError:
            raise AssertionError(f"Valor não numérico: {line!r}") from None
