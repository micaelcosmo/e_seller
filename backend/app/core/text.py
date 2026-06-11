"""Utilitário de texto: geração de slugs declarativos a partir de nomes."""

import re


class Slugifier:
    """Converte nomes/títulos em slugs estáveis (minúsculo, com hífens)."""

    def __init__(self, fallback: str = "item") -> None:
        """Define o slug de reserva quando o texto não gera caracteres válidos."""
        self.fallback = fallback

    def slugify(self, text: str) -> str:
        """Normaliza o texto para slug (a-z, 0-9 e hífens)."""
        lowered = text.strip().lower()
        replaced = re.sub(r"[^a-z0-9]+", "-", lowered)
        trimmed = replaced.strip("-")
        return trimmed or self.fallback
