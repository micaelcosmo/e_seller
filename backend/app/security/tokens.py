"""Geração de tokens seguros (downloads)."""

import secrets


class TokenFactory:
    """Gera tokens criptograficamente seguros e imprevisíveis."""

    def __init__(self, n_bytes: int = 32) -> None:
        """Define o número de bytes de entropia do token."""
        self.n_bytes = n_bytes

    def generate(self) -> str:
        """Retorna um token URL-safe único e seguro."""
        return secrets.token_urlsafe(self.n_bytes)
