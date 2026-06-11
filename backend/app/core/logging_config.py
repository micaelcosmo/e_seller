"""Configuração de logging estruturado (JSON) para o e_seller."""

from __future__ import annotations

import json
import logging
import time
from contextvars import ContextVar

# Variável de contexto compartilhada pelo middleware e pelo formatter.
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="-")


class JsonFormatter(logging.Formatter):
    """Formata cada entrada de log como uma linha JSON compacta."""

    def format(self, record: logging.LogRecord) -> str:
        """Serializa o LogRecord para um objeto JSON de linha única."""
        entry = {
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)
            ),
            "level": record.levelname,
            "correlation_id": correlation_id_var.get(),
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


class LoggingConfig:
    """Configura o root logger com saída JSON para stdout."""

    def __init__(self, level: str = "INFO") -> None:
        """Define o nível de log (padrão INFO)."""
        self.level = level

    def setup(self) -> None:
        """Substitui os handlers do root logger pelo handler JSON."""
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root = logging.getLogger()
        root.handlers.clear()
        root.addHandler(handler)
        root.setLevel(getattr(logging, self.level, logging.INFO))
