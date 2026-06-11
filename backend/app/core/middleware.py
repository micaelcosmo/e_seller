"""Middlewares da aplicação: correlation ID, security headers e process time."""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.core.logging_config import correlation_id_var


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adiciona cabeçalhos de segurança HTTP em todas as respostas.

    Inclui CSP (configurável), X-Content-Type-Options, X-Frame-Options,
    Referrer-Policy e HSTS (apenas quando hsts_max_age > 0 nas Settings).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Injeta os headers de segurança após processar a requisição."""
        response = await call_next(request)
        settings = get_settings()
        response.headers["Content-Security-Policy"] = settings.csp_header
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if settings.hsts_max_age > 0:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={settings.hsts_max_age}; includeSubDomains"
            )
        return response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """Adiciona o header X-Process-Time (em segundos) a toda resposta.

    Útil para monitorar latência sem precisar de instrumentação APM.
    """

    HEADER = "X-Process-Time"

    async def dispatch(self, request: Request, call_next) -> Response:
        """Mede o tempo de processamento e insere no header da resposta."""
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        response.headers[self.HEADER] = f"{elapsed:.6f}"
        return response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Lê ou gera X-Correlation-ID e o propaga via context var e header de resposta.

    Se o cliente enviar X-Correlation-ID, o valor é preservado (útil para rastreio
    ponta-a-ponta entre serviços). Caso contrário, gera um UUID v4.
    """

    HEADER = "X-Correlation-ID"

    async def dispatch(self, request: Request, call_next) -> Response:
        """Injeta o correlation ID no contexto e devolve no header da resposta."""
        cid = request.headers.get(self.HEADER) or str(uuid.uuid4())
        token = correlation_id_var.set(cid)
        try:
            response = await call_next(request)
            response.headers[self.HEADER] = cid
        finally:
            correlation_id_var.reset(token)
        return response
