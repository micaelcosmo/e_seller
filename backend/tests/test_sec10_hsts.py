"""Testes SEC-10: Strict-Transport-Security (HSTS) header configurável."""

from unittest.mock import patch

from app.core.config import Settings


async def test_hsts_ausente_por_padrao(client) -> None:
    """Por padrão (hsts_max_age=0), o header HSTS não é emitido."""
    resp = await client.get("/api/v1/healthz")
    assert resp.status_code == 200
    assert "strict-transport-security" not in resp.headers, (
        "HSTS não deve aparecer com hsts_max_age=0."
    )


async def test_hsts_presente_quando_configurado(client) -> None:
    """Quando hsts_max_age > 0, o header Strict-Transport-Security é emitido."""
    settings_with_hsts = Settings(hsts_max_age=31536000)
    with patch("app.core.middleware.get_settings", return_value=settings_with_hsts):
        resp = await client.get("/api/v1/healthz")
    assert resp.status_code == 200
    hsts = resp.headers.get("strict-transport-security", "")
    assert "max-age=31536000" in hsts, f"Header HSTS incorreto: {hsts!r}"
    assert "includeSubDomains" in hsts


async def test_outros_headers_de_seguranca_sempre_presentes(client) -> None:
    """Headers X-Frame-Options e X-Content-Type-Options estão sempre presentes."""
    resp = await client.get("/api/v1/healthz")
    assert resp.headers.get("x-frame-options") == "DENY"
    assert resp.headers.get("x-content-type-options") == "nosniff"
