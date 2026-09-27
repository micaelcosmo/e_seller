"""Middleware de proteção CSRF para formulários HTML (rotas web)."""

from __future__ import annotations

import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.types import ASGIApp

_COOKIE_NAME = "csrftoken"
_FIELD_NAME = "csrf_token"
_HEADER_NAME = "X-CSRF-Token"
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


class CSRFMiddleware(BaseHTTPMiddleware):
    """Protege rotas web (formulários HTML) contra ataques CSRF.

    Rotas da API (/api/) são isentas — autenticação JWT não usa cookies.
    Cada resposta GET define o cookie 'csrftoken' (legível por JS).
    POSTs para rotas web exigem que o campo oculto 'csrf_token' (ou o header
    X-CSRF-Token) contenha o mesmo valor do cookie.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Inicializa o middleware com a aplicação ASGI."""
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Gera o token em GETs; valida em POSTs de rotas web."""
        token = request.cookies.get(_COOKIE_NAME) or secrets.token_hex(32)
        request.state.csrf_token = token

        is_safe = request.method in _SAFE_METHODS
        is_api = request.url.path.startswith("/api/")

        if not is_safe and not is_api:
            form_token = ""
            header_token = request.headers.get(_HEADER_NAME, "")
            try:
                # body() guarda o corpo na requisição: o destino (ex.: o login do
                # SQLAdmin) recebe o mesmo formulário; form() sozinho o consumiria.
                await request.body()
                form_data = await request.form()
                form_token = str(form_data.get(_FIELD_NAME, ""))
            except Exception:
                pass
            submitted = form_token or header_token
            if not submitted or not secrets.compare_digest(submitted, token):
                return HTMLResponse("Token CSRF inválido.", status_code=403)

        response = await call_next(request)
        response.set_cookie(
            _COOKIE_NAME,
            token,
            httponly=False,
            samesite="lax",
        )
        return response
