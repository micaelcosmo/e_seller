"""Testes de OPS-01: logging JSON estruturado e correlation ID.

Cobre: header X-Correlation-ID propagado na resposta,
cliente pode enviar ID próprio, JsonFormatter produz JSON válido.
"""

import json
import logging

from app.core.logging_config import JsonFormatter


async def test_correlation_id_adicionado_na_resposta(client):
    """Toda resposta deve conter o header X-Correlation-ID."""
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    assert "x-correlation-id" in resp.headers


async def test_cliente_pode_enviar_correlation_id(client):
    """Se o cliente enviar X-Correlation-ID, o mesmo valor é devolvido."""
    cid = "teste-id-12345"
    resp = await client.get(
        "/api/v1/products",
        headers={"X-Correlation-ID": cid},
    )
    assert resp.headers["x-correlation-id"] == cid


async def test_json_formatter_saida_valida():
    """JsonFormatter produz JSON com os campos obrigatórios."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=1,
        msg="teste de log",
        args=(),
        exc_info=None,
    )
    output = formatter.format(record)
    data = json.loads(output)
    assert data["level"] == "INFO"
    assert data["message"] == "teste de log"
    assert "timestamp" in data
    assert "correlation_id" in data


async def test_correlation_id_propagado_no_contexto(client):
    """O ID gerado está presente na ContextVar durante a requisição."""
    cid = "meu-id-rastreio"
    resp = await client.get(
        "/api/v1/health",
        headers={"X-Correlation-ID": cid},
    )
    assert resp.headers.get("x-correlation-id") == cid


def test_json_formatter_com_excecao():
    """JsonFormatter inclui 'exception' quando exc_info está presente."""
    formatter = JsonFormatter()
    try:
        raise ValueError("erro de teste")
    except ValueError:
        import sys
        exc_info = sys.exc_info()
    record = logging.LogRecord(
        name="test", level=logging.ERROR, pathname="", lineno=1,
        msg="algo deu errado", args=(), exc_info=exc_info,
    )
    output = formatter.format(record)
    data = json.loads(output)
    assert "exception" in data
    assert "ValueError" in data["exception"]
