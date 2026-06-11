"""Rate limiting por IP ou user_id: janela de tempo deslizante (in-memory).

Implementação sem dependências externas. Para produção com múltiplas instâncias,
substitua o `_InMemoryStore` por um backend Redis.
"""

from __future__ import annotations

import time
from collections import deque

from fastapi import Depends, HTTPException, Request

from app.core.config import Settings, get_settings
from app.security.jwt import InvalidToken, JwtService


class _InMemoryStore:
    """Armazena timestamps de requisições por chave (IP + rota)."""

    def __init__(self) -> None:
        """Inicializa o dicionário compartilhado."""
        self._windows: dict[str, deque[float]] = {}

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Verifica e registra a requisição; retorna False se o limite foi excedido."""
        now = time.monotonic()
        cutoff = now - window_seconds
        if key not in self._windows:
            self._windows[key] = deque()
        window = self._windows[key]
        # Remove timestamps fora da janela (mais antigos que cutoff).
        while window and window[0] < cutoff:
            window.popleft()
        if len(window) >= max_requests:
            return False
        window.append(now)
        return True


class RateLimit:
    """Dependency chamável que aplica rate limiting por IP à rota atual.

    O store é lido de `request.app.state.rate_store` para que cada instância da
    aplicação (incluindo as de teste) tenha seu próprio estado — sem vazamento
    entre testes paralelos.

    Exemplo de uso:
        limit_5_per_min = RateLimit(max_requests=5, window_seconds=60)

        @router.post("/login")
        async def login(..., _: None = Depends(limit_5_per_min)):
            ...
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        """Define o limite e a janela de tempo."""
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def __call__(self, request: Request) -> None:
        """Aplica o limite; levanta 429 se excedido."""
        store: _InMemoryStore = request.app.state.rate_store
        ip = request.client.host if request.client else "unknown"
        key = f"ip:{ip}:{request.url.path}"
        allowed = store.is_allowed(key, self.max_requests, self.window_seconds)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Muitas requisições. Tente novamente mais tarde.",
            )


class LoginFailTracker:
    """Rastreia tentativas de login falhas por e-mail (proteção contra força bruta).

    Bloqueia temporariamente o e-mail após N falhas em uma janela de tempo.
    Estado mantido em app.state para isolamento entre instâncias de teste.
    """

    def __init__(self, max_failures: int = 5, window_seconds: int = 300) -> None:
        """Define o número máximo de falhas e a janela de tempo em segundos."""
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self._failures: dict[str, deque[float]] = {}

    def record_failure(self, email: str) -> None:
        """Registra uma tentativa de login falha para o e-mail informado."""
        now = time.monotonic()
        key = email.lower()
        if key not in self._failures:
            self._failures[key] = deque()
        self._failures[key].append(now)

    def is_blocked(self, email: str) -> bool:
        """Retorna True se o e-mail atingiu o limite de falhas na janela ativa."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        key = email.lower()
        if key not in self._failures:
            return False
        window = self._failures[key]
        while window and window[0] < cutoff:
            window.popleft()
        return len(window) >= self.max_failures


class AuthAwareRateLimit:
    """Dependency que aplica rate limit por user_id (autenticado) ou IP (anônimo).

    Evita bypass via IPv6/VPN em rotas onde o usuário pode estar logado: contas
    autenticadas são identificadas pelo 'sub' do JWT em vez do endereço de rede.
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        """Define o limite e a janela de tempo."""
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def __call__(
        self,
        request: Request,
        settings: Settings = Depends(get_settings),
    ) -> None:
        """Aplica o limite usando user:{sub} se autenticado, ip:{ip} se anônimo."""
        store: _InMemoryStore = request.app.state.rate_store
        key = self._build_key(request, settings)
        allowed = store.is_allowed(key, self.max_requests, self.window_seconds)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Muitas requisições. Tente novamente mais tarde.",
            )

    def _build_key(self, request: Request, settings: Settings) -> str:
        """Retorna chave user:{sub}:{path} se autenticado, ip:{ip}:{path} se não."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                jwt = JwtService(settings.app_secret_key)
                claims = jwt.verify(token)
                sub = claims.get("sub", "")
                if sub:
                    return f"user:{sub}:{request.url.path}"
            except InvalidToken:
                pass
        ip = request.client.host if request.client else "unknown"
        return f"ip:{ip}:{request.url.path}"
